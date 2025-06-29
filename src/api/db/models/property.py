from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.api.db.models.base import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    price = Column(Float, nullable=True)

    amenities = Column(JSON, nullable=True)
    num_rooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)

    available_from = Column(TIMESTAMP(timezone=False), nullable=True)
    available_to = Column(TIMESTAMP(timezone=False), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
