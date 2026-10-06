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

import json
import os
import urllib.request
from typing import Any


def get_live_exchange_rates(base_currency: str = "USD") -> dict[str, Any]:
    """Fetches real-time live exchange rates for budget travel planning using a public finance API.

    Args:
        base_currency: The 3-letter currency code to fetch rates relative to (e.g. 'USD', 'EUR', 'GBP').

    Returns:
        A dictionary containing live exchange rates, date, base currency, and status.
    """
    # Reads optional API key from environment variable if provided
    api_key = os.environ.get("CURRENCY_API_KEY", "")
    base_code = base_currency.upper().strip()

    try:
        url = f"https://api.frankfurter.app/latest?from={base_code}"
        headers = {"User-Agent": "GlobeTrotter/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return {
                "status": "success",
                "base": data.get("base", base_code),
                "date": data.get("date"),
                "rates": data.get("rates", {}),
                "api_key_configured": bool(api_key),
            }
    except Exception as err:
        return {
            "status": "error",
            "message": f"Failed to fetch live rates for {base_code}: {err}",
            "base": base_code,
        }
