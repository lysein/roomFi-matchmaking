from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PropertyBase(BaseModel):
    owner_id: int
    address: str
    location: Optional[str]
    price: float
    amenities: Optional[List[str]] = []
    num_rooms: int
    bathrooms: int
    available_from: Optional[datetime]
    available_to: Optional[datetime]

class PropertyCreate(PropertyBase):
    pass

class PropertyOut(PropertyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
