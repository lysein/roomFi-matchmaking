from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from sqlalchemy.sql import func
from .base import Base

class RoomieGroup(Base):
    __tablename__ = "roomie_groups"

    id = Column(Integer, primary_key=True)
    members = Column(ARRAY(Integer))  # list of user_ids
    status = Column(String, default="pending")  # pending, matched, staked, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
