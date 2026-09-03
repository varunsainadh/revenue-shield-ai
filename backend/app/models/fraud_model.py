from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
import uuid
from app.database import Base

class FraudAlertModel(Base):
    __tablename__ = "fraud_alerts"

    id = Column(String, primary_key=True, default=lambda: f"fa_{uuid.uuid4().hex[:10]}")
    transaction_id = Column(String, index=True, nullable=True)
    customer_id = Column(String, index=True, nullable=True)
    alert_type = Column(String, nullable=False, index=True) # REFUND_ABUSE, DUPLICATE_REFUND, REFUND_SPIKE, UNUSUAL_BEHAVIOR
    severity = Column(String, nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=True)
    status = Column(String, default="OPEN", index=True) # OPEN, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
