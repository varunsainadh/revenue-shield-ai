from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class RefundCreateRequest(BaseModel):
    payment_id: str
    amount: float
    reason: Optional[str] = "Customer request"

class RefundResponse(BaseModel):
    id: str
    payment_id: str
    customer_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    reason: Optional[str] = None
    is_suspicious: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
