from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .preferences import RoomiePreferences

class UserBase(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name_1: str
    last_name_2: str
    email: EmailStr
    gender: Optional[str]
    age: Optional[int]
    lgbtq: Optional[bool] = False
    budget_min: Optional[float]
    budget_max: Optional[float]
    location_preference: Optional[str]
    lifestyle_tags: Optional[List[str]] = []
    roomie_preferences: Optional[RoomiePreferences]

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
