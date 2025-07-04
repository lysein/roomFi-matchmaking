from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import ARRAY
from src.api.db.models.base import Base

class LandlordProfile(Base):
    __tablename__ = "landlord_profile"

    id = Column(Integer, primary_key=True, index=True)  # 👈 Surrogate key
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)  # 👈 FK to auth.users

    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)

    verified = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    preferred_locations = Column(ARRAY(String), nullable=True)
    
    num_properties = Column(Integer, nullable=True, default=0)
