from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class FraudAlertResponse(BaseModel):
    id: str
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    alert_type: str
    severity: str
    description: str
    evidence_json: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FraudAlertResolveRequest(BaseModel):
    status: str = "RESOLVED" # RESOLVED or DISMISSED
    resolution_notes: Optional[str] = "Handled by merchant operator"
