# src/api/db/schemas/landlord.py

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class LandlordProfileOut(BaseModel):
    id: int
    user_id: UUID
    clabe: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    verified: Optional[bool]
    bio: Optional[str]
    profile_image_url: Optional[HttpUrl]
    joined_at: Optional[datetime]
    preferred_locations: Optional[List[str]]
    num_properties: Optional[int]

    class Config:
        orm_mode = True
