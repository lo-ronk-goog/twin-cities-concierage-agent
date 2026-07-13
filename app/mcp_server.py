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

import asyncio
import json
import logging
from google.cloud import bigquery
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bigquery_mcp_server")

# Create the MCP Server
mcp_server = Server("msp-bigquery-mcp")

@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List tools available on this MCP server."""
    return [
        types.Tool(
            name="bigquery_query",
            description="Executes a read-only SQL query against the Google Cloud BigQuery database to verify venue availability, vibes, hours, and events.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The standard SELECT SQL query to execute. E.g., SELECT * FROM `lpr-gemini-enterprise-1.msp_coffee_and_music.venues` LIMIT 10"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Execute a tool call request."""
    if name != "bigquery_query":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        return [types.TextContent(type="text", text="Error: query parameter is required")]

    # Enforce read-only constraint for safety
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        return [types.TextContent(type="text", text="Error: Only SELECT and WITH queries are allowed for security reasons.")]

    try:
        # Initialize standard BigQuery client (uses default auth credentials)
        client = bigquery.Client()
        query_job = client.query(query)
        results = query_job.result()
        
        # Serialize rows
        rows = [dict(row) for row in results]
        return [types.TextContent(type="text", text=json.dumps(rows, default=str))]
    except Exception as e:
        logger.error(f"BigQuery execution error: {e}")
        return [types.TextContent(type="text", text=f"BigQuery Error: {str(e)}")]

async def main():
    """Run the MCP server using standard I/O streams."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="msp-bigquery-mcp",
                server_version="1.0.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability(listChanged=True)
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
