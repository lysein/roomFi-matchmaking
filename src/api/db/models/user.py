from sqlalchemy import Column, Integer, String, Float, Text, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from src.api.db.models.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)

    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)

    location_preference = Column(String, nullable=True)

    lifestyle_tags = Column(JSON, nullable=True)
    roomie_preferences = Column(JSON, nullable=True)

    bio = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
