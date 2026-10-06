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

import base64
import uuid
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded constants as required
PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
BUCKET_NAME = "globetrotter-budget-assets-qwiklabs-gcp-03-60573bb34fdb"
MODEL_NAME = "gemini-omni-flash-preview"
LOCATION = "global"


async def generate_destination_video(
    destination_name: str,
    tool_context: ToolContext,
    prompt_details: str = "A vibrant scenic video preview of a budget travel destination with local culture and atmosphere",
) -> dict[str, Any]:
    """Generates a short travel video preview using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as a session artifact and uploads it to public Cloud Storage.

    Args:
        destination_name: Name of the travel destination or attraction (e.g., 'Bangkok, Thailand').
        tool_context: ADK ToolContext automatically injected by the runner.
        prompt_details: Details about the scene or atmosphere for the video generation.

    Returns:
        A dictionary containing the public Cloud Storage HTTPS URL of the video.
    """
    clean_slug = destination_name.lower().strip().replace(" ", "_").replace(",", "")
    unique_id = uuid.uuid4().hex[:8]
    object_name = f"videos/{clean_slug}_{unique_id}.mp4"
    artifact_filename = f"{clean_slug}_{unique_id}.mp4"

    # 1. Generate video using gemini-omni-flash-preview model in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    prompt = f"A short travel video preview of {destination_name}. {prompt_details}."

    video_bytes = None
    mime_type = "video/mp4"

    # Try Interactions API (Gemini Omni model)
    try:
        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
        )
        if hasattr(interaction, "output_video") and interaction.output_video and getattr(interaction.output_video, "data", None):
            raw_data = interaction.output_video.data
            if isinstance(raw_data, str):
                video_bytes = base64.b64decode(raw_data)
            elif isinstance(raw_data, bytes):
                video_bytes = raw_data
    except Exception:
        # Fallback to generate_content or inline parts if model supports modal content parts
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["VIDEO"],
                ),
            )
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        raw_data = part.inline_data.data
                        if isinstance(raw_data, str):
                            video_bytes = base64.b64decode(raw_data)
                        else:
                            video_bytes = raw_data
                        mime_type = part.inline_data.mime_type or "video/mp4"
                        break
        except Exception as e:
            return {"status": "error", "message": f"Failed to generate video for {destination_name}: {e}"}

    if not video_bytes:
        return {"status": "error", "message": f"No video bytes generated for {destination_name}"}

    # 2. Save video with tool_context.save_artifact for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    try:
        await tool_context.save_artifact(
            filename=artifact_filename,
            artifact=artifact_part,
            custom_metadata={"destination": destination_name, "model": MODEL_NAME},
        )
    except Exception:
        # Artifact service may be uninitialized in test environments
        pass

    # 3. Upload video bytes to public Cloud Storage bucket (no local file created)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "destination": destination_name,
        "video_url": public_url,
        "artifact_filename": artifact_filename,
    }
