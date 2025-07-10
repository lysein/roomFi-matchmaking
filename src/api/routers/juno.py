from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
import httpx
import time
import hmac
import hashlib
from src.api.config import settings
from typing import Optional

router = APIRouter()

JUNO_API_KEY = settings.JUNO_API_KEY
JUNO_API_SECRET = settings.JUNO_API_SECRET
JUNO_BASE_URL = settings.JUNO_BASE_URL

def sign_juno_request(method: str, path: str):
    nonce = str(int(time.time() * 1000))  # milliseconds
    data = f"{nonce}{method}{path}"
    signature = hmac.new(JUNO_API_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    authorization = f"Bitso {JUNO_API_KEY}:{nonce}:{signature}"
    return authorization

@router.post("/create-clabe")
async def create_clabe():
    try:
        method = "POST"
        path = "/mint_platform/v1/clabes"
        url = f"{JUNO_BASE_URL}{path}"
        authorization = sign_juno_request(method, path)

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers={"Authorization": authorization})

        if not (200 <= response.status_code < 300):
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clabe/{clabe}/details")
async def get_clabe_details(clabe: str):
    try:
        method = "GET"
        path = f"/spei/v1/clabes/{clabe}"
        url = f"{JUNO_BASE_URL}{path}"

        authorization = sign_juno_request(method, path)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"Authorization": authorization})

        if not (200 <= response.status_code < 300):
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clabe/list")
async def list_clabes(
    clabe_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: Optional[int] = Query(None),
    page_size: Optional[int] = Query(None)
):
    try:
        method = "GET"
        path = "/spei/v1/clabes"

        # Build query string dynamically based on provided parameters
        query_params = []
        if clabe_type:
            query_params.append(f"clabe_type={clabe_type}")
        if start_date:
            query_params.append(f"start_date={start_date}")
        if end_date:
            query_params.append(f"end_date={end_date}")
        if page:
            query_params.append(f"page={page}")
        if page_size:
            query_params.append(f"page_size={page_size}")

        query_string = "&".join(query_params)
        url = f"{JUNO_BASE_URL}{path}"
        if query_string:
            url = f"{url}?{query_string}"

        authorization = sign_juno_request(method, path)  # Signature uses path only (no query)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"Authorization": authorization})

        if not (200 <= response.status_code < 300):
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))