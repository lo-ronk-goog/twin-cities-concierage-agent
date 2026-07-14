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

import os
import logging
import requests
import google.auth
import google.auth.transport.requests
from google.adk.tools import FunctionTool

logger = logging.getLogger("app.tools")

def execute_sql_readonly(query: str) -> str:
    """Execute a read-only SELECT SQL query on the BigQuery database to retrieve venue, event, and hours information.
    
    Args:
        query: The read-only SELECT SQL query to execute.
    """
    # Resolve project ID
    try:
        _, project = google.auth.default()
    except Exception:
        project = "lpr-gemini-enterprise-1"
        
    if not project:
        project = "lpr-gemini-enterprise-1"

    # Acquire and refresh Google Cloud credentials for the HTTP request
    try:
        credentials, _ = google.auth.default()
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        token = credentials.token
    except Exception as auth_err:
        logger.error(f"Authentication error in execute_sql_readonly: {auth_err}", exc_info=True)
        return f"Authentication error: {auth_err}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-goog-user-project": project
    }

    url = "https://bigquery.googleapis.com/mcp"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_sql_readonly",
            "arguments": {
                "project_id": project,
                "query": query
            }
        },
        "id": 1
    }
    
    try:
        logger.info(f"Calling BigQuery MCP endpoint for query: {query}")
        response = requests.post(url, headers=headers, json=payload)
        return response.text
    except Exception as e:
        logger.error(f"Error calling BigQuery MCP: {e}", exc_info=True)
        return f"Error calling MCP: {e}"

# Register the Python function as an ADK FunctionTool
execute_sql_tool = FunctionTool(execute_sql_readonly)
