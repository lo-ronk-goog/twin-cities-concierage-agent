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

import google.auth
from google.adk.tools import FunctionTool
from google.auth.transport.requests import AuthorizedSession

logger = logging.getLogger("app.tools")


def execute_sql_readonly(query: str) -> str:
    """Execute a read-only SELECT SQL query on the BigQuery database to retrieve venue, event, and hours information.

    Args:
        query: The read-only SELECT SQL query to execute.
    """
    # Resolve project ID and credentials with cloud-platform scope
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    except Exception:
        credentials = None
        project = "lpr-gemini-enterprise-1"

    if not project:
        project = "lpr-gemini-enterprise-1"

    url = "https://bigquery.googleapis.com/mcp"
    headers = {
        "Content-Type": "application/json",
        "x-goog-user-project": project,
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_sql_readonly",
            "arguments": {"project_id": project, "query": query},
        },
        "id": 1,
    }

    try:
        logger.info(f"Calling BigQuery MCP endpoint for query: {query}")
        session = AuthorizedSession(credentials) if credentials else None
        if session:
            response = session.post(url, headers=headers, json=payload)
        else:
            import requests

            response = requests.post(url, headers=headers, json=payload)
        return response.text
    except Exception as e:
        logger.error(f"Error calling BigQuery MCP: {e}", exc_info=True)
        return f"Error calling MCP: {e}"


# Register the Python function as an ADK FunctionTool
execute_sql_tool = FunctionTool(execute_sql_readonly)
