from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PropertyBase(BaseModel):
    owner_id: int
    address: str
    location: Optional[str]
    price: float
    property_type: Optional[str]
    num_rooms: int
    bathrooms: int
    deposit_months: Optional[int]
    contract_length_months: Optional[int]
    amenities: Optional[List[str]] = []
    amenidad_extras: Optional[List[str]] = []
    parking: Optional[bool]
    security_features: Optional[List[str]] = []
    available_from: Optional[datetime]
    available_to: Optional[datetime]

class PropertyCreate(PropertyBase):
    pass

class PropertyOut(PropertyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
