from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class UserProfileOut(BaseModel):
    id: int
    user_id: UUID
    clabe: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    email: Optional[EmailStr]
    gender: Optional[str]
    age: Optional[int]
    budget_min: Optional[float]
    budget_max: Optional[float]
    location_preference: Optional[str]
    lifestyle_tags: Optional[List[str]]
    roomie_preferences: Optional[Dict[str, Any]]
    bio: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    profile_image_url: Optional[HttpUrl]

    class Config:
        orm_mode = True
