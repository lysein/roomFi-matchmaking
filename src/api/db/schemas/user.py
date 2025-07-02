# src/api/schemas/user.py

from pydantic import BaseModel, UUID4
from typing import Optional, List

class UserProfileCreate(BaseModel):
    user_id: UUID4
    first_name: str
    last_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location_preference: Optional[str] = None
    lifestyle_tags: Optional[List[str]] = None
    roomie_preferences: Optional[dict] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

    class Config:
        extra = "forbid"
