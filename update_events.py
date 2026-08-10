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

    sql_query = f"""
    DECLARE max_date DATE;
    SET max_date = (SELECT MAX(PARSE_DATE('%Y-%B-%d', event_date)) FROM `{FULL_TABLE_ID}`);

    UPDATE `{FULL_TABLE_ID}`
    SET event_date = FORMAT_DATE('%Y-%B-%d', DATE_ADD(PARSE_DATE('%Y-%B-%d', event_date), INTERVAL DATE_DIFF(DATE('2026-08-16'), max_date, DAY) DAY))
    WHERE TRUE;
    """

    logger.info("Executing date-shift query in BigQuery...")
    try:
        query_job = client.query(sql_query)
        # Wait for the query to complete
        query_job.result()
        logger.info(
            "Successfully shifted all event dates to current week (August 10 - August 16, 2026)!"
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
