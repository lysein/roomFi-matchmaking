from fastapi import APIRouter, HTTPException
from datetime import datetime
from src.api.db.schemas.user import UserProfileCreate
from src.api.config import client

router = APIRouter()

@router.post("/user")
def create_user_profile(payload: UserProfileCreate):
    # Check if profile already exists
    existing = client.table("user_profiles").select("user_id").eq("user_id", str(payload.user_id)).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="User profile already exists")

    # Insert new profile
    result = client.table("user_profiles").insert({
        "user_id": str(payload.user_id),
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "gender": payload.gender,
        "age": payload.age,
        "budget_min": payload.budget_min,
        "budget_max": payload.budget_max,
        "location_preference": payload.location_preference,
        "lifestyle_tags": payload.lifestyle_tags,
        "roomie_preferences": payload.roomie_preferences,
        "bio": payload.bio,
        "profile_image_url": payload.profile_image_url,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return {"message": "User profile created", "user_id": payload.user_id}
