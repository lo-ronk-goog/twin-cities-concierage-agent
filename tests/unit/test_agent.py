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

from app.agent import root_agent, app
from app.tools import bigquery_mcp_toolset

def test_agent_config():
    """Verify that the agent is initialized with correct instructions and tools."""
    assert root_agent.name == "twin_cities_concierage_agent"
    assert "concierge" in root_agent.instruction.lower()
    assert "jazz" in root_agent.instruction.lower()
    assert "coffee" in root_agent.instruction.lower()
    
    # Check that MCP toolset is registered
    assert bigquery_mcp_toolset in root_agent.tools
    assert len(root_agent.tools) == 1

def test_app_config():
    """Verify that the App correctly registers the root agent."""
    assert app.name == "app"
    assert app.root_agent == root_agent
