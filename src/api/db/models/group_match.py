from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from .base import Base

class GroupMatch(Base):
    __tablename__ = "group_matches"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("roomie_groups.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    match_score = Column(Float)
    status = Column(String, default="suggested")  # suggested, shortlisted, staked, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
