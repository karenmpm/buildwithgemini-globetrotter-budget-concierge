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

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback
from app.budget_tools import calculate_budget_breakdown
from app.currency_tools import convert_currency
from app.firestore_tools import (
    add_budget_destination,
    get_destination_details,
    search_budget_destinations,
)
from app.image_tools import generate_destination_image
from app.live_currency_tools import get_live_exchange_rates
from app.postcard_tools import generate_destination_postcard
from app.video_tools import generate_destination_video

PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
MEMORY_BANK_ID = "4858399110392184832"

# Build A2UI 0.8 system prompt
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "GlobeTrotter, an expert AI travel concierge specializing in budget travel and affordable adventures. "
        "Help travelers discover budget-friendly destinations, hostels, top attractions, currency conversions, real-time live exchange rates, and average daily cost breakdowns. "
        "You remember user preferences and facts from previous conversations and use them to personalize recommendations. "
        "You have access to a secure Python sandbox code executor to safely run calculations and data processing code. "
        "Use the budget destination tools to search, view details, calculate budget breakdowns, convert currency, fetch live exchange rates, generate postcard images, generate destination postcards, generate short destination videos, and add new budget travel destinations."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

# Configure Agent Engine Sandbox Code Executor from deployment_metadata.json
deployment_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
code_executor = None

if deployment_metadata_path.exists():
    try:
        with open(deployment_metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        sandbox_res = metadata.get("sandbox_resource_name")
        agent_engine_res = metadata.get("remote_agent_runtime_id")
        if sandbox_res:
            code_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=sandbox_res)
        elif agent_engine_res:
            code_executor = AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_res)
    except Exception:
        pass

if not code_executor:
    code_executor = AgentEngineSandboxCodeExecutor()


# Memory callback: after each turn, extract durable facts to Vertex AI Memory Bank
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


# Memory service builder for Cloud deployment runtime
def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-central1",
        agent_engine_id=MEMORY_BANK_ID,
    )


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        search_budget_destinations,
        get_destination_details,
        add_budget_destination,
        calculate_budget_breakdown,
        generate_destination_image,
        convert_currency,
        get_live_exchange_rates,
        generate_destination_postcard,
        generate_destination_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
