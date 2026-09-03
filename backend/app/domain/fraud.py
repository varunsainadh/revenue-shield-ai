from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.domain.enums import FraudAlertType, FraudSeverity, FraudAlertStatus

class FraudAlertDomain(BaseModel):
    id: Optional[str] = None
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    alert_type: FraudAlertType
    severity: FraudSeverity
    description: str
    evidence: Dict[str, Any]
    status: FraudAlertStatus = FraudAlertStatus.OPEN
    created_at: datetime = datetime.utcnow()
