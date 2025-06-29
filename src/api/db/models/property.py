from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from src.api.db.models.base import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String)
    location = Column(String)  # optional, can expand to lat/lng
    price = Column(Float)
    amenities = Column(JSON)  # e.g. ["wifi", "laundry", "balcony"]
    num_rooms = Column(Integer)
    bathrooms = Column(Integer)
    available_from = Column(DateTime)
    available_to = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
