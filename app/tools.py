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
import google.auth
from google.adk.integrations.agent_registry import AgentRegistry

logger = logging.getLogger("app.tools")

try:
    _, project_id = google.auth.default()
except Exception:
    project_id = "lpr-gemini-enterprise-1"

location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

try:
    # Initialize the AgentRegistry
    registry = AgentRegistry(project_id=project_id, location=location)
    
    # Load the Google-managed remote BigQuery MCP Server registered in Gemini Enterprise
    bigquery_mcp_toolset = registry.get_mcp_toolset(
        "projects/lpr-gemini-enterprise-1/locations/global/mcpServers/agentregistry-00000000-0000-0000-eb30-f0665e1792d1"
    )
except Exception as e:
    logger.warning(f"Failed to load remote MCP Toolset: {e}. Falling back to empty stub for test compilation.")
    # Fallback to local stub to allow offline tests to compile and import without credentials
    import sys
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    
    bigquery_mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=["-c", "import sys; sys.exit(0)"],
            )
        ),
        tool_filter=["bigquery_query"]
    )
