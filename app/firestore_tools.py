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

from typing import Any, Optional
from google.cloud import firestore

# Hardcoded GCP Project ID as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
COLLECTION_NAME = "budget_destinations"


def _get_firestore_db() -> firestore.Client:
    """Helper to initialize the Firestore client with hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_budget_destinations(
    max_daily_cost_usd: Optional[float] = None,
    country: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Searches the Firestore database for budget travel destinations.

    Args:
        max_daily_cost_usd: Optional maximum average daily cost in USD to filter by.
        country: Optional country name to filter destinations by (case-insensitive search).

    Returns:
        A list of matching destination dictionaries.
    """
    db = _get_firestore_db()
    docs = db.collection(COLLECTION_NAME).stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Apply client-side filters for safety and flexibility
        if max_daily_cost_usd is not None:
            if data.get("avg_daily_cost_usd", 9999) > max_daily_cost_usd:
                continue

        if country is not None and country.strip():
            doc_country = data.get("country", "").lower()
            if country.lower() not in doc_country:
                continue

        results.append(data)

    return results


def get_destination_details(destination_id: str) -> dict[str, Any]:
    """Retrieves full details for a specific budget travel destination by ID or slug.

    Args:
        destination_id: The document ID/slug of the destination (e.g. 'bangkok-thailand').

    Returns:
        A dictionary containing destination details or an error dictionary if not found.
    """
    db = _get_firestore_db()
    doc_ref = db.collection(COLLECTION_NAME).document(destination_id.lower().strip())
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Fallback search by name
    docs = db.collection(COLLECTION_NAME).stream()
    for doc in docs:
        data = doc.to_dict()
        if data.get("name", "").lower() == destination_id.lower().strip():
            data["id"] = doc.id
            return data

    return {"error": f"Destination '{destination_id}' not found in budget destinations database."}


def add_budget_destination(
    name: str,
    country: str,
    avg_daily_cost_usd: float,
    hostel_avg_nightly_usd: float,
    budget_category: str,
    top_attractions: list[str],
    description: str,
) -> dict[str, Any]:
    """Adds a new budget travel destination to the Firestore catalog.

    Args:
        name: Name of the destination city or region.
        country: Country where the destination is located.
        avg_daily_cost_usd: Estimated average daily cost per traveler in USD.
        hostel_avg_nightly_usd: Estimated nightly hostel or budget lodging cost in USD.
        budget_category: Category (e.g., 'super-budget', 'moderate-budget').
        top_attractions: List of key attractions or activities.
        description: Brief highlight description of the destination.

    Returns:
        A dictionary confirming the newly created destination document.
    """
    db = _get_firestore_db()
    doc_id = f"{name.lower().strip().replace(' ', '-')}-{country.lower().strip().replace(' ', '-')}"

    destination_data = {
        "id": doc_id,
        "name": name,
        "country": country,
        "avg_daily_cost_usd": avg_daily_cost_usd,
        "hostel_avg_nightly_usd": hostel_avg_nightly_usd,
        "budget_category": budget_category,
        "top_attractions": top_attractions,
        "description": description,
    }

    db.collection(COLLECTION_NAME).document(doc_id).set(destination_data)
    return {"status": "success", "message": f"Successfully added {name}, {country} to budget destinations.", "destination": destination_data}
