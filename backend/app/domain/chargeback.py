from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.enums import RiskLevel

class ChargebackFactor(BaseModel):
    factor: str
    impact: str # HIGH, MEDIUM, LOW
    description: str

class ChargebackPredictionDomain(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    risk_score: int # 0 - 100
    risk_level: RiskLevel
    confidence: float
    top_risk_factors: List[ChargebackFactor]
    explanation: str
    created_at: datetime = datetime.utcnow()
