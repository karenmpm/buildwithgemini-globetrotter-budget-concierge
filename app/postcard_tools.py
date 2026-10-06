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

import uuid
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded constants as required
PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
BUCKET_NAME = "globetrotter-budget-assets-qwiklabs-gcp-03-60573bb34fdb"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_destination_postcard(
    destination_name: str,
    tool_context: ToolContext,
    prompt_details: str = "scenic budget travel destination postcard with vibrant local atmosphere",
) -> dict[str, Any]:
    """Generates an image for a budget travel item using gemini-3.1-flash-lite-image in the global region.

    Saves the image as a session artifact and uploads it to public Cloud Storage.

    Args:
        destination_name: Name of the travel destination or item (e.g., 'Bangkok, Thailand').
        tool_context: ADK ToolContext automatically injected by the runner.
        prompt_details: Description or atmosphere details for the image prompt.

    Returns:
        A dictionary containing the public Cloud Storage HTTPS URL.
    """
    clean_slug = destination_name.lower().strip().replace(" ", "_").replace(",", "")
    unique_id = uuid.uuid4().hex[:8]
    object_name = f"postcards/{clean_slug}_{unique_id}.jpg"
    artifact_filename = f"{clean_slug}_{unique_id}.jpg"

    # 1. Generate image using gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    prompt = f"A beautiful travel postcard photo of {destination_name}. {prompt_details}."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return {"status": "error", "message": f"Failed to generate image bytes for {destination_name}"}

    # 2. Save image with tool_context.save_artifact for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    try:
        await tool_context.save_artifact(
            filename=artifact_filename,
            artifact=artifact_part,
            custom_metadata={"destination": destination_name, "model": MODEL_NAME},
        )
    except ValueError:
        # Artifact service may be uninitialized in unit test runners
        pass

    # 3. Upload image bytes to public Cloud Storage bucket (no local file created)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "destination": destination_name,
        "image_url": public_url,
        "artifact_filename": artifact_filename,
    }
