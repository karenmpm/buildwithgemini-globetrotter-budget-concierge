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

from typing import Any


def calculate_budget_breakdown(
    total_budget_usd: float,
    num_days: int,
    lodging_style: str = "hostel",
) -> dict[str, Any]:
    """Calculates daily expense caps and itemized spending allocation for a budget trip.

    Args:
        total_budget_usd: Total amount allocated for the trip in USD.
        num_days: Duration of the trip in days.
        lodging_style: Preference for lodging: 'hostel' (shared dorm), 'private_room' (budget hotel), or 'homestay'.

    Returns:
        A dictionary with calculated daily caps, category allocations (lodging, food, transport, activities), and emergency buffer.
    """
    if num_days <= 0 or total_budget_usd <= 0:
        return {"error": "Total budget and number of days must be greater than zero."}

    # Reserve 10% emergency buffer
    emergency_buffer = round(total_budget_usd * 0.10, 2)
    spendable_budget = total_budget_usd - emergency_buffer

    daily_max_usd = round(spendable_budget / num_days, 2)

    # Allocation ratios based on lodging style
    style_clean = lodging_style.lower().strip()
    if "private" in style_clean or "hotel" in style_clean:
        lodging_ratio, food_ratio, transport_ratio, activity_ratio = 0.45, 0.30, 0.12, 0.13
    elif "homestay" in style_clean:
        lodging_ratio, food_ratio, transport_ratio, activity_ratio = 0.40, 0.35, 0.12, 0.13
    else:  # hostel dorm default
        lodging_ratio, food_ratio, transport_ratio, activity_ratio = 0.35, 0.35, 0.15, 0.15

    daily_lodging = round(daily_max_usd * lodging_ratio, 2)
    daily_food = round(daily_max_usd * food_ratio, 2)
    daily_transport = round(daily_max_usd * transport_ratio, 2)
    daily_activities = round(daily_max_usd * activity_ratio, 2)

    return {
        "total_budget_usd": total_budget_usd,
        "num_days": num_days,
        "lodging_style": lodging_style,
        "emergency_buffer_usd": emergency_buffer,
        "spendable_budget_usd": round(spendable_budget, 2),
        "daily_max_usd": daily_max_usd,
        "daily_breakdown_usd": {
            "lodging": daily_lodging,
            "food_and_drinks": daily_food,
            "local_transport": daily_transport,
            "activities_and_sightseeing": daily_activities,
        },
        "total_breakdown_usd": {
            "lodging": round(daily_lodging * num_days, 2),
            "food_and_drinks": round(daily_food * num_days, 2),
            "local_transport": round(daily_transport * num_days, 2),
            "activities_and_sightseeing": round(daily_activities * num_days, 2),
        },
    }
