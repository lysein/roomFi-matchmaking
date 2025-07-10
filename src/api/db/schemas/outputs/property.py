from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class PropertyOut(BaseModel):
    id: int
    owner_user_id: UUID
    clabe: str
    address: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    price: float
    amenities: List[str]
    num_rooms: int
    bathrooms: int
    available_from: datetime
    available_to: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True