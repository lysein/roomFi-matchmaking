# src/api/schemas/landlord.py

from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class LandlordProfileCreate(BaseModel):
    user_id: UUID4
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    verified: Optional[bool] = False
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    joined_at: Optional[datetime] = None
    preferred_locations: Optional[List[str]] = None

    class Config:
        extra = "forbid"