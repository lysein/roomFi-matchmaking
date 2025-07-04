from pydantic import BaseModel, UUID4, Field, Extra
from typing import List
from datetime import datetime

class PropertyCreate(BaseModel):
    owner_user_id: UUID4
    address: str
    location: str
    price: float
    amenities: List[str]
    num_rooms: int
    bathrooms: int
    available_from: datetime
    available_to: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        extra = "forbid"  # 🚫 Reject extra keys not defined above
