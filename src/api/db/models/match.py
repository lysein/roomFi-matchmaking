from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
from src.api.db.models.base import Base
from enum import Enum

class MatchStatusEnum(str, Enum):
    pending = "pending"
    matched = "matched"
    rejected = "rejected"
    expired = "expired"

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    matched_user_id = Column(UUID(as_uuid=True), nullable=True)
    matched_property_id = Column(Integer, nullable=True)

    score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    status = Column(PgEnum(MatchStatusEnum, name="match_status_enum"), nullable=True)
    source = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
