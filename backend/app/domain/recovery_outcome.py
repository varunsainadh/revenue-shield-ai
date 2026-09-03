from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecoveryOutcomeDomain(BaseModel):
    case_id: str
    recovered: bool
    recovered_amount: float
    channel_used: Optional[str] = None
    time_to_recover_minutes: Optional[float] = None
    attempts_count: int = 1
    created_at: datetime = datetime.utcnow()
