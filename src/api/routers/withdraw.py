import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr, condecimal
import time
import hmac
import hashlib
import httpx

from src.api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

API_KEY = settings.JUNO_API_KEY
API_SECRET = settings.JUNO_API_SECRET
BASE_URL = settings.JUNO_BASE_URL

class WithdrawalRequest(BaseModel):
    address: constr(min_length=10)
    amount: condecimal(gt=0)
    asset: str = "MXNB"
    blockchain: str = "ARBITRUM"

def exact_postman_body(address, amount, asset, blockchain):
    return (
        '{"address":"%s","amount":"%s","asset":"%s","blockchain":"%s","compliance":{"travel_rule":{}}}'
        % (address, amount, asset, blockchain)
    )

def sign_postman_style(method: str, path: str, body_str: str):
    nonce = str(int(time.time() * 1000))
    data = f"{nonce}{method}{path}{body_str}"
    signature = hmac.new(API_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    authorization = f"Bitso {API_KEY}:{nonce}:{signature}"
    return authorization

@router.post("/withdraw")
async def withdraw_funds(req: WithdrawalRequest):
    try:
        logger.info("Received withdrawal request: %s", req.dict())

        method = "POST"
        path = "/mint_platform/v1/withdrawals"
        url = f"{BASE_URL}{path}"

        body_str = exact_postman_body(
            req.address,
            str(req.amount),
            req.asset,
            req.blockchain
        )
        logger.info("Constructed request body: %s", body_str)

        authorization = sign_postman_style(method, path, body_str)
        logger.info("Generated authorization header.")

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "User-Agent": "PostmanRuntime/7.44.1",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate, br"
        }
        logger.info("Headers prepared for the request.")

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            logger.info("Sending POST request to %s", url)
            response = await client.post(
                url,
                headers=headers,
                content=body_str.encode()
            )

        logger.info("Received response with status code: %d", response.status_code)
        logger.debug("Response content: %s", response.text)

        if not (200 <= response.status_code < 300):
            logger.error("Withdrawal failed: %s", response.text)
            raise HTTPException(status_code=502, detail=f"Withdrawal failed: {response.text}")

        logger.info("Withdrawal successful.")
        return JSONResponse(status_code=response.status_code, content=response.json())

    except Exception as e:
        logger.exception("An error occurred during the withdrawal process.")
        raise HTTPException(status_code=500, detail=str(e))
