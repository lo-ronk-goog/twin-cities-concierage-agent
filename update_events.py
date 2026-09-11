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


def shift_event_dates():
    logger.info("Initializing BigQuery Client...")
    client = bigquery.Client(project=PROJECT_ID)

    # Automatically shifts all dates to the current week (ending this coming Sunday),
    # preserving day-of-week alignment and storing dates in standard ISO YYYY-MM-DD format.
    sql_query = f"""
    DECLARE target_sunday DATE;
    DECLARE max_date DATE;

    -- Target Sunday of current week (Monday=day 1 ... Sunday=day 7)
    SET target_sunday = DATE_ADD(DATE_TRUNC(CURRENT_DATE(), WEEK(MONDAY)), INTERVAL 6 DAY);

    -- Detect max date whether stored as YYYY-MM-DD or YYYY-MonthName-DD
    SET max_date = (
        SELECT MAX(
            CASE
                WHEN REGEXP_CONTAINS(event_date, r'^\\d{{4}}-\\d{{2}}-\\d{{2}}$')
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
                WHEN REGEXP_CONTAINS(event_date, r'^\\d{{4}}-\\d{{2}}-\\d{{2}}$')
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
            "Successfully shifted all event dates to current week (YYYY-MM-DD)!"
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
    shift_event_dates()
