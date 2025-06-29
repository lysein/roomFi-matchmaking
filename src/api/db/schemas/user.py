from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    gender: Optional[str]
    age: Optional[int]
    budget_min: Optional[float]
    budget_max: Optional[float]
    location_preference: Optional[str]
    lifestyle_tags: Optional[List[str]] = []
    roomie_preferences: Optional[Dict[str, str]] = {}

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
