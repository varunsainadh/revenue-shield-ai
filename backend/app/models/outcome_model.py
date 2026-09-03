from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class RecoveryOutcomeModel(Base):
    __tablename__ = "recovery_outcomes"

    id = Column(String, primary_key=True, default=lambda: f"out_{uuid.uuid4().hex[:10]}")
    recovery_case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False, index=True)
    recovered = Column(Boolean, nullable=False, default=False)
    recovered_amount = Column(Float, default=0.0)
    channel_used = Column(String, nullable=True)
    time_to_recover_minutes = Column(Float, nullable=True)
    attempts_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("RecoveryCaseModel", back_populates="outcomes")
