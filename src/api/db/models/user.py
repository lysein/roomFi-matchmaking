from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from src.api.db.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    gender = Column(String)
    age = Column(Integer)
    budget_min = Column(Float)
    budget_max = Column(Float)
    location_preference = Column(String)
    lifestyle_tags = Column(JSON)  # e.g., ["early_riser", "likes_pets"]
    roomie_preferences = Column(JSON)  # e.g., {"gender": "female", "cleanliness": "high"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
