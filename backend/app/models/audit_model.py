from sqlalchemy import Column, String, Float, DateTime, Text
from datetime import datetime
import uuid
from app.database import Base

class AuditModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: f"aud_{uuid.uuid4().hex[:10]}")
    case_id = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String, nullable=False, index=True)
    actor = Column(String, default="SYSTEM")
    action = Column(String, nullable=False)
    previous_state = Column(String, nullable=True)
    new_state = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    policy_rule = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
