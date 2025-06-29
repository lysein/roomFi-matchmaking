from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Stake(Base):
    __tablename__ = "stakes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("roomie_groups.id"))
    amount_mxn = Column(Float)
    confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    txn_id = Column(String)  # Juno or other payment system ref
