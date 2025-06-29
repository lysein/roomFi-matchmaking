from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from src.api.config import settings

router = APIRouter()
security = HTTPBearer()

SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode failed")

@router.get("/me", summary="Get current authenticated user")
def read_current_user(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
