# ruff: noqa
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
import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools import execute_sql_tool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.agents.callback_context import CallbackContext

# CI/CD Trigger: Testing merge path and validation pipeline run.
try:
    _, default_project_id = google.auth.default()
except Exception:
    default_project_id = "lpr-gemini-enterprise-1"

project_id = (
    os.environ.get("GOOGLE_CLOUD_PROJECT")
    or default_project_id
    or "lpr-gemini-enterprise-1"
)
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get(
    "GOOGLE_CLOUD_LOCATION", "us-central1"
)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger = logging.getLogger("app.agent")

persona_instruction = (
    "You are a friendly, expert local concierge for the Minneapolis-Twin Cities area. "
    "Your goal is to help users plan the perfect day or night out, specifically focusing on "
    "coffee shops, casual bars, and live jazz venues. You must always verify venue operating hours, "
    "locations, and live music schedules before making a recommendation. Do not guess or hallucinate venue information. "
    "Always format your final recommendations beautifully as structured lists with emojis for clarity.\n\n"
    "You have access to a Google Cloud BigQuery database containing venue, event, and operating hours data.\n"
    "The dataset is `lpr-gemini-enterprise-1.msp_coffee_and_music`.\n"
    "Tables:\n"
    "1. `venues`: Contains `venue_id`, `name`, `city`, `neighborhood`, `category`, and `vibe`.\n"
    "2. `operating_hours`: Contains `venue_id`, `day_of_week`, `open_time`, and `close_time`.\n"
    "3. `events`: Contains `event_id`, `venue_id`, `event_date`, `artist`, `genre`, and `start_time`.\n\n"
    "When you need to look up venue, event, or operating hours data, invoke the `execute_sql_readonly` tool "
    "with a valid BigQuery SQL query in the `query` argument (e.g. querying `lpr-gemini-enterprise-1.msp_coffee_and_music.venues`). "
    "Never output raw SQL code to the user."
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Orchestrates memory generation by sending the session history to the Memory Bank."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        logger.warning(
            "Memory service not available or error adding session to memory: %s", e
        )
    return None


root_agent = Agent(
    name="twin_cities_concierge_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=persona_instruction,
    tools=[execute_sql_tool, PreloadMemoryTool()],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
