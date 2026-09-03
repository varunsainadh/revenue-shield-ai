from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ChargebackFactorSchema(BaseModel):
    factor: str
    impact: str
    description: str

class ChargebackPredictionResponse(BaseModel):
    id: str
    transaction_id: str
    customer_id: str
    amount: float
    risk_score: int
    risk_level: str
    confidence: float
    top_risk_factors_json: str
    explanation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChargebackPredictRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    payment_method: Optional[str] = "UPI"
    previous_failure_count: Optional[int] = 0
    is_first_time_customer: Optional[bool] = False
    failure_reason: Optional[str] = "incorrect_pin"
