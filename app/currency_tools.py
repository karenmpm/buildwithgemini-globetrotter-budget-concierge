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

# Standard exchange rates relative to 1 USD for popular budget destinations
EXCHANGE_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 0.92,
    "THB": 36.5,     # Thai Baht
    "VND": 25400.0,  # Vietnamese Dong
    "MXN": 18.2,     # Mexican Peso
    "HUF": 365.0,    # Hungarian Forint
    "JPY": 155.0,    # Japanese Yen
    "IDR": 16200.0,  # Indonesian Rupiah
    "INR": 83.5,     # Indian Rupee
    "GBP": 0.78,     # British Pound
}


def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "THB",
) -> dict[str, Any]:
    """Converts a budget travel amount between common currencies.

    Args:
        amount: The monetary amount to convert.
        from_currency: Three-letter currency code to convert from (e.g. 'USD', 'EUR').
        to_currency: Three-letter currency code to convert to (e.g. 'THB', 'VND', 'MXN', 'HUF').

    Returns:
        A dictionary containing the converted amount, exchange rate, and currency details.
    """
    from_code = from_currency.upper().strip()
    to_code = to_currency.upper().strip()

    if from_code not in EXCHANGE_RATES_TO_USD:
        return {"error": f"Unsupported currency '{from_code}'. Supported: {list(EXCHANGE_RATES_TO_USD.keys())}"}
    if to_code not in EXCHANGE_RATES_TO_USD:
        return {"error": f"Unsupported currency '{to_code}'. Supported: {list(EXCHANGE_RATES_TO_USD.keys())}"}

    # Convert to USD base first, then to target currency
    amount_in_usd = amount / EXCHANGE_RATES_TO_USD[from_code]
    converted_amount = round(amount_in_usd * EXCHANGE_RATES_TO_USD[to_code], 2)
    effective_rate = round(EXCHANGE_RATES_TO_USD[to_code] / EXCHANGE_RATES_TO_USD[from_code], 4)

    return {
        "original_amount": amount,
        "from_currency": from_code,
        "converted_amount": converted_amount,
        "to_currency": to_code,
        "effective_rate": effective_rate,
    }
