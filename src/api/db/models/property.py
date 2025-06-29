from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from .base import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String)
    location = Column(String)
    price = Column(Float)
    property_type = Column(String)  # "casa" or "departamento"
    num_rooms = Column(Integer)
    bathrooms = Column(Integer)
    deposit_months = Column(Integer)
    contract_length_months = Column(Integer)
    amenities = Column(JSON)
    amenidad_extras = Column(JSON)
    parking = Column(Boolean)
    security_features = Column(JSON)
    available_from = Column(DateTime)
    available_to = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
