from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchBase(BaseModel):
    user_id: int
    matched_user_id: Optional[int]
    matched_property_id: Optional[int]
    score: float
    status: Optional[str] = "pending"

class MatchCreate(MatchBase):
    pass

class MatchOut(MatchBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
