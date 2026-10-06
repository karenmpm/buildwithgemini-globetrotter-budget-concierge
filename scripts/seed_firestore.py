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

from google.cloud import firestore

# Hardcoded GCP Project ID as requested to prevent Agent Platform lookup errors
PROJECT_ID = "qwiklabs-gcp-03-60573bb34fdb"
COLLECTION_NAME = "budget_destinations"

SEED_DESTINATIONS = [
    {
        "id": "bangkok-thailand",
        "name": "Bangkok",
        "country": "Thailand",
        "avg_daily_cost_usd": 35,
        "budget_category": "super-budget",
        "hostel_avg_nightly_usd": 12,
        "top_attractions": ["Grand Palace", "Wat Arun", "Chatuchak Market", "Khao San Road"],
        "best_months_to_visit": ["November", "December", "January", "February"],
        "description": "Vibrant street food capital with iconic temples, bustling night markets, and ultra-affordable hostels.",
    },
    {
        "id": "hanoi-vietnam",
        "name": "Hanoi",
        "country": "Vietnam",
        "avg_daily_cost_usd": 30,
        "budget_category": "super-budget",
        "hostel_avg_nightly_usd": 9,
        "top_attractions": ["Old Quarter", "Hoan Kiem Lake", "Train Street", "Ha Long Bay Day Trip"],
        "best_months_to_visit": ["October", "November", "March", "April"],
        "description": "Charming ancient city famous for $1 egg coffee, incredible street cuisine, and budget homestays.",
    },
    {
        "id": "budapest-hungary",
        "name": "Budapest",
        "country": "Hungary",
        "avg_daily_cost_usd": 55,
        "budget_category": "moderate-budget",
        "hostel_avg_nightly_usd": 22,
        "top_attractions": ["Buda Castle", "Ruin Bars", "Széchenyi Thermal Bath", "Fisherman's Bastion"],
        "best_months_to_visit": ["May", "June", "September", "October"],
        "description": "One of Europe's most affordable architectural gems, famous for grand thermal baths and vibrant ruin bars.",
    },
    {
        "id": "oaxaca-mexico",
        "name": "Oaxaca",
        "country": "Mexico",
        "avg_daily_cost_usd": 40,
        "budget_category": "super-budget",
        "hostel_avg_nightly_usd": 15,
        "top_attractions": ["Monte Albán", "Santo Domingo Church", "Hierve el Agua", "Mercado 20 de Noviembre"],
        "best_months_to_visit": ["October", "November", "December", "January"],
        "description": "Cultural culinary heart of Mexico known for mezcal tastings, mole, Zapotec ruins, and affordable artisan markets.",
    },
    {
        "id": "lisbon-portugal",
        "name": "Lisbon",
        "country": "Portugal",
        "avg_daily_cost_usd": 65,
        "budget_category": "moderate-budget",
        "hostel_avg_nightly_usd": 28,
        "top_attractions": ["Belém Tower", "Tram 28", "Alfama District", "Sintra Day Trip"],
        "best_months_to_visit": ["April", "May", "September", "October"],
        "description": "Sun-drenched coastal capital with historic tramways, pastel houses, world-class hostels, and cheap pastel de nata.",
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding items into collection '{COLLECTION_NAME}'...")
    for item in SEED_DESTINATIONS:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  - Seeded: {item['name']}, {item['country']} (Doc ID: {doc_id})")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed()
