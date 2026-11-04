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

from app.tools import execute_sql_tool, query_brunch_tool
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
    "GOOGLE_CLOUD_LOCATION", "global"
)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = os.environ.get(
    "GOOGLE_API_USE_CLIENT_CERTIFICATE", "false"
)

logger = logging.getLogger("app.agent")

# Model Armor Configuration (defense-in-depth against prompt injection / jailbreak)
model_armor_project = os.environ.get("MODEL_ARMOR_PROJECT", project_id)
model_armor_location = os.environ.get("MODEL_ARMOR_LOCATION", "us-central1")
model_armor_template_id = os.environ.get(
    "MODEL_ARMOR_TEMPLATE_ID", "standard-template-for-prompts"
)

if model_armor_template_id.startswith("projects/"):
    model_armor_template_name = model_armor_template_id
else:
    model_armor_template_name = (
        f"projects/{model_armor_project}/locations/{model_armor_location}/templates/{model_armor_template_id}"
    )

MODEL_ARMOR_BLOCKED_MESSAGE = (
    "🛡️ [Model Armor Guardrail]: Your request was blocked because it triggered "
    "prompt security and safety policies (e.g., prompt injection or jailbreak detection)."
)

_model_armor_plugin_registered = False


async def model_armor_guardrail_callback(
    callback_context: CallbackContext, llm_request
):
    """Screens user prompts with Model Armor before dispatching to the LLM.

    Provides in-app defense-in-depth sanitization to secure streaming (:streamQuery)
    interactions when ingress gateway hooks are bypassed (platform issue b/555399867).
    """
    if _model_armor_plugin_registered:
        return None

    try:
        from google.adk.models import LlmResponse
        from google.api_core import client_options
        from google.cloud import modelarmor_v1

        if not llm_request or not getattr(llm_request, "contents", None):
            return None

        # Extract text from the latest user prompt
        last_turn = llm_request.contents[-1]
        text_parts = [
            p.text
            for p in getattr(last_turn, "parts", [])
            if getattr(p, "text", None)
        ]
        if not text_parts:
            return None
        prompt_text = " ".join(text_parts)

        endpoint = f"modelarmor.{model_armor_location}.rep.googleapis.com"
        opts = client_options.ClientOptions(api_endpoint=endpoint)
        client = modelarmor_v1.ModelArmorAsyncClient(client_options=opts)

        request = modelarmor_v1.SanitizeUserPromptRequest(
            name=model_armor_template_name,
            user_prompt_data=modelarmor_v1.DataItem(text=prompt_text),
        )
        response = await client.sanitize_user_prompt(request=request)
        result = getattr(response, "sanitization_result", None)

        if (
            result
            and getattr(result, "filter_match_state", None)
            == modelarmor_v1.FilterMatchState.MATCH_FOUND
        ):
            logger.warning(
                "Model Armor in-app guardrail intercepted prompt injection/jailbreak: %s",
                result,
            )
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(MODEL_ARMOR_BLOCKED_MESSAGE)],
                )
            )
    except Exception as e:
        # Graceful fail-open for local dev / unauthenticated environments
        logger.warning(
            "Model Armor in-app check bypassed or service unavailable: %s", e
        )
    return None


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
    "For brunch menus and weekend specials, you can also invoke the `query_brunch_specials` tool. "
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
        model="gemini-3.8-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=persona_instruction,
    tools=[execute_sql_tool, query_brunch_tool, PreloadMemoryTool()],
    before_model_callback=model_armor_guardrail_callback,
    after_agent_callback=generate_memories_callback,
)

plugins = []

try:
    from google.adk.integrations.model_armor import ModelArmorConfig, ModelArmorPlugin

    model_armor_plugin = ModelArmorPlugin(
        config=ModelArmorConfig(
            prompt_template_name=model_armor_template_name,
            block_on_screening_failure=False,
            input_blocked_message=MODEL_ARMOR_BLOCKED_MESSAGE,
        )
    )
    plugins.append(model_armor_plugin)
    _model_armor_plugin_registered = True
    logger.info(
        "Registered ADK ModelArmorPlugin for template: %s",
        model_armor_template_name,
    )
except Exception as e:
    logger.info(
        "Native ModelArmorPlugin not loaded (%s); using fallback before_model_callback.",
        e,
    )

app = App(
    root_agent=root_agent,
    name="app",
    plugins=plugins,
)
