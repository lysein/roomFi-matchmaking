# src/api/services/juno.py

import httpx
import time
import hmac
import hashlib
from src.api.config import settings

JUNO_API_KEY = settings.JUNO_API_KEY
JUNO_API_SECRET = settings.JUNO_API_SECRET
JUNO_BASE_URL = settings.JUNO_BASE_URL

def sign_juno_request(method: str, path: str):
    nonce = str(int(time.time() * 1000))  # milliseconds
    data = f"{nonce}{method}{path}"
    signature = hmac.new(JUNO_API_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    authorization = f"Bitso {JUNO_API_KEY}:{nonce}:{signature}"
    return authorization

async def create_clabe_for_user():
    method = "POST"
    path = "/mint_platform/v1/clabes"
    url = f"{JUNO_BASE_URL}{path}"
    authorization = sign_juno_request(method, path)

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(url, headers={"Authorization": authorization})
        if not (200 <= response.status_code < 300):
            raise Exception("Failed to create CLABE for user")
        resp_json = response.json()
        clabe = resp_json.get("payload", {}).get("clabe")
        if not clabe:
            raise Exception("CLABE response missing clabe")
        return clabe
