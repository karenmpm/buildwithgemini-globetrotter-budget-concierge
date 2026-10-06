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

import io
import uuid
from typing import Any
from PIL import Image, ImageDraw, ImageEnhance
from google import genai
from google.genai import types
from google.cloud import storage

# Hardcoded GCP Project ID and Bucket Name as requested
PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
BUCKET_NAME = "globetrotter-budget-assets-qwiklabs-gcp-03-60573bb34fdb"


def _upload_to_gcs(image_bytes: bytes, filename_prefix: str) -> str:
    """Uploads image bytes to public Cloud Storage bucket and returns the public URL."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)

    blob_name = f"postcards/{filename_prefix}_{uuid.uuid4().hex[:8]}.jpg"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    return f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"


def _create_styled_postcard(destination_name: str, caption: str) -> bytes:
    """Generates a high-resolution, vibrant stylized travel postcard image card."""
    width, height = 900, 600
    
    # Create base gradient canvas (sunset / ocean aesthetic)
    base = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(base)

    # Vibrant sunset gradient (Deep Navy -> Warm Coral -> Golden Amber)
    for y in range(height):
        r = int(15 + (245 - 15) * (y / height))
        g = int(23 + (158 - 23) * (y / height))
        b = int(42 + (11 - 42) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add geometric aesthetic waves and mountain silhouette accents
    draw.ellipse([(-100, 350), (1000, 850)], fill=(255, 255, 255, 20))
    draw.polygon([(0, 600), (300, 380), (600, 600)], fill=(15, 23, 42))
    draw.polygon([(400, 600), (650, 420), (900, 600)], fill=(30, 41, 59))

    # Add semi-transparent card overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Bottom banner card
    overlay_draw.rectangle([(40, 420), (width - 40, 560)], fill=(15, 23, 42, 220), outline=(245, 158, 11, 255), width=3)
    
    # Top badge tag
    overlay_draw.rectangle([(50, 50), (320, 100)], fill=(245, 158, 11, 240))

    # Merge overlay with base image
    composite = Image.alpha_composite(base.convert("RGBA"), overlay)
    draw_final = ImageDraw.Draw(composite)

    # Text renderings
    draw_final.text((70, 62), "GLOBETROTTER", fill=(15, 23, 42))
    draw_final.text((60, 440), destination_name.upper(), fill=(255, 255, 255))
    draw_final.text((60, 500), f"✨ {caption}", fill=(245, 158, 11))

    # Convert to JPEG bytes
    buffer = io.BytesIO()
    composite.convert("RGB").save(buffer, format="JPEG", quality=92)
    return buffer.getvalue()


def generate_destination_image(
    destination_name: str,
    caption: str = "Explore budget-friendly sights & local culture",
) -> dict[str, Any]:
    """Generates a visual postcard image for a travel destination and uploads it to public GCS.

    Args:
        destination_name: Name of the destination city or country (e.g. 'Bangkok, Thailand').
        caption: Short highlight caption to display on the visual postcard.

    Returns:
        A dictionary containing the public GCS URL of the generated image.
    """
    image_bytes = None
    source = "ai_generated"

    # Attempt AI Image Generation via Imagen on Vertex AI
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
        prompt = f"A vibrant high-resolution travel postcard photo of {destination_name}, featuring iconic local landmarks, budget travel aesthetic, warm golden lighting."
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/jpeg"),
        )
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
    except Exception:
        # Fallback to high-quality stylized travel postcard generator
        source = "stylized_postcard_generator"
        image_bytes = _create_styled_postcard(destination_name, caption)

    clean_slug = destination_name.lower().strip().replace(" ", "_").replace(",", "")
    public_url = _upload_to_gcs(image_bytes, clean_slug)

    return {
        "status": "success",
        "destination": destination_name,
        "image_url": public_url,
        "source": source,
        "message": f"Successfully generated postcard for {destination_name} and published to GCS.",
    }
