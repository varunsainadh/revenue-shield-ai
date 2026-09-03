from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class PromiseToPayModel(Base):
    __tablename__ = "promises_to_pay"

    id = Column(String, primary_key=True, default=lambda: f"ptp_{uuid.uuid4().hex[:10]}")
    recovery_case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False, index=True)
    customer_id = Column(String, index=True, nullable=False)
    promised_date = Column(DateTime, nullable=False)
    status = Column(String, default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    case = relationship("RecoveryCaseModel", back_populates="promises")
