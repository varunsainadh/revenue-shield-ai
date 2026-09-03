from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class RecoveryCaseModel(Base):
    __tablename__ = "recovery_cases"

    id = Column(String, primary_key=True, default=lambda: f"rc_{uuid.uuid4().hex[:10]}")
    transaction_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    payment_method = Column(String, nullable=False)
    bank = Column(String, nullable=True)
    hour_of_day = Column(Integer, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    
    failure_reason = Column(String, nullable=False)
    failure_category = Column(String, nullable=False)
    previous_success_count = Column(Integer, default=0)
    previous_failure_count = Column(Integer, default=0)
    customer_success_rate = Column(Float, default=0.0)
    attempt_number = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    gateway_latency_ms = Column(Integer, default=0)
    device_type = Column(String, default="mobile")
    risk_level = Column(String, default="LOW")
    
    status = Column(String, default="OPEN", index=True)
    
    recoverability_score = Column(Float, nullable=True)
    recommended_channel = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    recommended_erv = Column(Float, nullable=True)
    channel_scores_json = Column(Text, nullable=True)
    
    policy_result = Column(String, nullable=True)
    policy_reason = Column(Text, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_attempt_at = Column(DateTime, nullable=True)
    recovered_at = Column(DateTime, nullable=True)

    promises = relationship("PromiseToPayModel", back_populates="case", cascade="all, delete-orphan")
    outcomes = relationship("RecoveryOutcomeModel", back_populates="case", cascade="all, delete-orphan")
    payment_links = relationship("PaymentLinkModel", back_populates="case", cascade="all, delete-orphan")
