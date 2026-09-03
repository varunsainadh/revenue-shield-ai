from sqlalchemy import Column, String, Float, Boolean, DateTime
from datetime import datetime
import uuid
from app.database import Base

class RefundModel(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True, default=lambda: f"rf_{uuid.uuid4().hex[:10]}")
    payment_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="PROCESSED", index=True)
    reason = Column(String, nullable=True)
    is_suspicious = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
