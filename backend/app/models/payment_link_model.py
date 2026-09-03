from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class PaymentLinkModel(Base):
    __tablename__ = "payment_links"

    id = Column(String, primary_key=True, default=lambda: f"plink_{uuid.uuid4().hex[:10]}")
    bound_case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False, index=True)
    invoice_reference = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    razorpay_link_id = Column(String, nullable=True, index=True)
    url = Column(String, nullable=False)
    status = Column(String, default="CREATED", index=True) # CREATED, PAID, EXPIRED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    case = relationship("RecoveryCaseModel", back_populates="payment_links")
