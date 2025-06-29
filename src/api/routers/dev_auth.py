from fastapi import APIRouter, HTTPException
import requests
from pydantic import BaseModel
from src.api.config import settings

router = APIRouter()

SUPABASE_AUTH_URL = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
HEADERS = {
    "apikey": settings.SUPABASE_ANON_KEY,
    "Content-Type": "application/json",
}


class Credentials(BaseModel):
    email: str
    password: str


@router.post("/token", summary="Get Supabase access token (local dev only)")
def get_access_token(credentials: Credentials):
    response = requests.post(
        SUPABASE_AUTH_URL,
        headers=HEADERS,
        json={"email": credentials.email, "password": credentials.password},
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return response.json()
