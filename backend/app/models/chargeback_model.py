from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from datetime import datetime
import uuid
from app.database import Base

class ChargebackPredictionModel(Base):
    __tablename__ = "chargeback_predictions"

    id = Column(String, primary_key=True, default=lambda: f"cb_{uuid.uuid4().hex[:10]}")
    transaction_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    risk_score = Column(Integer, nullable=False) # 0 - 100
    risk_level = Column(String, nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, default=0.85)
    top_risk_factors_json = Column(Text, nullable=False) # JSON array of factors
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
