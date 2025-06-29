from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    last_name_1 = Column(String, nullable=False)
    last_name_2 = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    gender = Column(String)
    age = Column(Integer)
    lgbtq = Column(Boolean, default=False)
    budget_min = Column(Float)
    budget_max = Column(Float)
    location_preference = Column(String)
    lifestyle_tags = Column(JSON)
    roomie_preferences = Column(JSON)  # Will be validated with Pydantic schema
    created_at = Column(DateTime(timezone=True), server_default=func.now())
