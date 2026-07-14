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
from google.adk.tools.base_toolset import BaseToolset

logger = logging.getLogger("app.tools")

class LazyRegistryToolset(BaseToolset):
    """Lazily loads the Agent Registry MCP toolset at runtime to avoid import-time API calls."""
    def __init__(self, mcp_server_name: str):
        super().__init__()
        self.mcp_server_name = mcp_server_name
        self._toolset = None

    def get_tools(self, context=None):
        if self._toolset is None:
            from google.adk.integrations.agent_registry import AgentRegistry
            import google.auth
            
            try:
                _, project_id = google.auth.default()
            except Exception:
                project_id = "lpr-gemini-enterprise-1"
                
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
            logger.info(f"Lazily loading Agent Registry MCP server '{self.mcp_server_name}' in region '{location}'...")
            
            try:
                registry = AgentRegistry(project_id=project_id, location=location)
                toolset = registry.get_mcp_toolset(self.mcp_server_name)
                # Remove prefix so tools map exactly as execute_sql_readonly
                toolset.tool_name_prefix = ""
                self._toolset = toolset
            except Exception as registry_err:
                logger.error(
                    f"CRITICAL: Failed to load remote Agent Registry toolset '{self.mcp_server_name}' "
                    f"in project '{project_id}' and region '{location}': {registry_err}",
                    exc_info=True
                )
                raise registry_err
            
        return self._toolset.get_tools(context)

# Initialize the lazy toolset wrapping our Google-managed remote BigQuery MCP server
bigquery_mcp_toolset = LazyRegistryToolset(
    "projects/lpr-gemini-enterprise-1/locations/global/mcpServers/agentregistry-00000000-0000-0000-eb30-f0665e1792d1"
)
