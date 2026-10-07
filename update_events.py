# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from google.auth.exceptions import RefreshError
from google.cloud import bigquery

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ID = "lpr-gemini-enterprise-1"
DATASET_NAME = "msp_coffee_and_music"
TABLE_NAME = "events"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}"


def shift_event_dates(target_sunday_str: str | None = None, populate_all_october: bool = False):
    logger.info("Initializing BigQuery Client...")
    client = bigquery.Client(project=PROJECT_ID)

    if populate_all_october:
        # Replicates events across all 4 weekends of October 2026
        # Week 1: Oct 01 - Oct 04 (ends Sun Oct 04)
        # Week 2: Oct 08 - Oct 11 (ends Sun Oct 11)
        # Week 3: Oct 15 - Oct 18 (ends Sun Oct 18)
        # Week 4: Oct 22 - Oct 25 (ends Sun Oct 25)
        logger.info("Generating events across all 4 weeks of October 2026...")
        sql_query = f"""
        CREATE OR REPLACE TABLE `{FULL_TABLE_ID}` AS
        WITH base_events AS (
            SELECT
                event_id,
                venue_id,
                artist,
                genre,
                start_time,
                CASE
                    WHEN REGEXP_CONTAINS(event_date, r'^\d{{4}}-\d{{2}}-\d{{2}}$')
                    THEN PARSE_DATE('%Y-%m-%d', event_date)
                    ELSE PARSE_DATE('%Y-%B-%d', event_date)
                END AS parsed_date
            FROM `{FULL_TABLE_ID}`
        ),
        normalized_week1 AS (
            SELECT
                event_id,
                venue_id,
                artist,
                genre,
                start_time,
                DATE_ADD(
                    parsed_date,
                    INTERVAL DATE_DIFF(DATE('2026-10-04'), (SELECT MAX(parsed_date) FROM base_events), DAY) DAY
                ) AS event_date_week1
            FROM base_events
        ),
        all_weeks AS (
            SELECT
                event_id, venue_id, artist, genre, start_time,
                FORMAT_DATE('%Y-%m-%d', event_date_week1) AS event_date
            FROM normalized_week1
            UNION ALL
            SELECT
                CONCAT(event_id, '-W2'), venue_id, artist, genre, start_time,
                FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 7 DAY)) AS event_date
            FROM normalized_week1
            UNION ALL
            SELECT
                CONCAT(event_id, '-W3'), venue_id, artist, genre, start_time,
                FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 14 DAY)) AS event_date
            FROM normalized_week1
            UNION ALL
            SELECT
                CONCAT(event_id, '-W4'), venue_id, artist, genre, start_time,
                FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 21 DAY)) AS event_date
            FROM normalized_week1
        )
        SELECT * FROM all_weeks;
        """
    else:
        # Automatically shifts all dates to current week or user-specified Sunday
        sunday_expr = (
            f"DATE('{target_sunday_str}')"
            if target_sunday_str
            else "DATE_ADD(DATE_TRUNC(CURRENT_DATE(), WEEK(MONDAY)), INTERVAL 6 DAY)"
        )

        sql_query = f"""
        DECLARE target_sunday DATE;
        DECLARE max_date DATE;

        SET target_sunday = {sunday_expr};

        -- Detect max date whether stored as YYYY-MM-DD or YYYY-MonthName-DD
        SET max_date = (
            SELECT MAX(
                CASE
                    WHEN REGEXP_CONTAINS(event_date, r'^\d{{4}}-\d{{2}}-\d{{2}}$')
                    THEN PARSE_DATE('%Y-%m-%d', event_date)
                    ELSE PARSE_DATE('%Y-%B-%d', event_date)
                END
            )
            FROM `{FULL_TABLE_ID}`
        );

        UPDATE `{FULL_TABLE_ID}`
        SET event_date = FORMAT_DATE(
            '%Y-%m-%d',
            DATE_ADD(
                CASE
                    WHEN REGEXP_CONTAINS(event_date, r'^\d{{4}}-\d{{2}}-\d{{2}}$')
                    THEN PARSE_DATE('%Y-%m-%d', event_date)
                    ELSE PARSE_DATE('%Y-%B-%d', event_date)
                END,
                INTERVAL DATE_DIFF(target_sunday, max_date, DAY) DAY
            )
        )
        WHERE TRUE;
        """

    logger.info("Executing date-shift query in BigQuery...")
    try:
        query_job = client.query(sql_query)
        # Wait for the query to complete
        query_job.result()
        logger.info(
            "Successfully updated event dates in BigQuery!"
        )
    except RefreshError:
        logger.error(
            "Google Cloud credentials expired or missing. Please run:\n"
            "    gcloud auth application-default login\n"
            "and try again."
        )
    except Exception as e:
        logger.error(f"Failed to execute BigQuery update: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update BigQuery event dates for October 2026")
    parser.add_argument(
        "--target-sunday",
        type=str,
        default=None,
        help="Specific Sunday date to align the weekend with (e.g. 2026-10-04, 2026-10-11)",
    )
    parser.add_argument(
        "--all-october",
        action="store_true",
        help="Replicate events across all 4 weeks of October 2026",
    )
    args = parser.parse_args()

    shift_event_dates(
        target_sunday_str=args.target_sunday,
        populate_all_october=args.all_october,
    )
