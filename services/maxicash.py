# API URL: "https://webapi-test.maxicashapp.com/Integration/PayNowSync"
""""
    MaxiCash Payment Integration Service
    Documentation: https://www.maxicashapp.com/developers"""

import os
import httpx
import requests
from typing import Dict, Any

MERCHANT_ID = os.getenv("MAXICASH_MERCHANT_ID")
MERCHANT_PASSWORD = os.getenv("MAXICASH_MERCHANT_PASSWORD")

async def send_payment_async(
    endpoint_url: str,
    request_data: Dict[str, Any],
    pay_type: int,
    currency_code: str,
    timeout: int = 10
) -> Dict[str, Any]:
    payload = {
        "RequestData": request_data,
        "MerchantID": MERCHANT_ID,
        "MerchantPassword": MERCHANT_PASSWORD,
        "PayType": pay_type,
        "CurrencyCode": currency_code
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(endpoint_url, json=payload, headers=headers)
            resp.raise_for_status()
            try:
                data = resp.json()
            except ValueError:
                data = {"raw_text": resp.text}
            return {"ok": True, "status_code": resp.status_code, "response": data}
        except httpx.RequestError as e:
            return {"ok": False, "error": str(e)}
        except httpx.HTTPStatusError as e:
            # accès à e.response si tu veux plus de détails
            return {"ok": False, "status_code": e.response.status_code, "error": e.response.text}
