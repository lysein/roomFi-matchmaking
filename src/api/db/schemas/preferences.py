from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class MoveInRange(BaseModel):
    start: date
    end: date

class RoomiePreferences(BaseModel):
    property_type: Optional[str]  # "casa", "departamento"
    move_in_range: Optional[MoveInRange]
    pet_friendly: Optional[bool]
    lgbtq_only: Optional[bool]
    amenities: Optional[List[str]] = []
    amenidad_extras: Optional[List[str]] = []
    parking: Optional[bool]
