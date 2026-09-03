from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChannelScoreDetail(BaseModel):
    probability: float
    erv: float
    simulated_cost: float = 0.0

class ChannelScores(BaseModel):
    email: ChannelScoreDetail
    whatsapp: ChannelScoreDetail
    voice: ChannelScoreDetail

class AgentRecommendation(BaseModel):
    failure_category: str
    recoverability_score: float
    channel_scores: Dict[str, ChannelScoreDetail]
    recommended_channel: str
    recommended_action: str
    confidence: float
    risk_level: str
    reason: str
    policy_result: Optional[str] = None
    policy_reason: Optional[str] = None

class RecoveryCaseCreate(BaseModel):
    transaction_id: str
    customer_id: str
    customer_email: Optional[str] = "customer@example.com"
    customer_phone: Optional[str] = "+919876543210"
    amount: float
    currency: str = "INR"
    payment_method: str = "UPI"
    bank: Optional[str] = "HDFC"
    failure_reason: str
    hour_of_day: Optional[int] = 14
    day_of_week: Optional[int] = 2
    previous_success_count: Optional[int] = 5
    previous_failure_count: Optional[int] = 1
    customer_success_rate: Optional[float] = 0.833
    gateway_latency_ms: Optional[int] = 250
    device_type: Optional[str] = "mobile"
    risk_level: Optional[str] = "LOW"

class RecoveryCaseResponse(BaseModel):
    id: str
    transaction_id: str
    customer_id: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    amount: float
    currency: str
    payment_method: str
    bank: Optional[str] = None
    hour_of_day: Optional[int] = None
    day_of_week: Optional[int] = None
    failure_reason: str
    failure_category: str
    previous_success_count: int
    previous_failure_count: int
    customer_success_rate: float
    attempt_number: int
    max_attempts: int
    gateway_latency_ms: int
    device_type: str
    risk_level: str
    status: str
    recoverability_score: Optional[float] = None
    recommended_channel: Optional[str] = None
    recommended_action: Optional[str] = None
    recommended_erv: Optional[float] = None
    channel_scores_json: Optional[str] = None
    policy_result: Optional[str] = None
    policy_reason: Optional[str] = None
    ai_reasoning: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_attempt_at: Optional[datetime] = None
    recovered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PromiseToPayCreate(BaseModel):
    promised_date: datetime

class PromiseToPayResponse(BaseModel):
    id: str
    recovery_case_id: str
    customer_id: str
    promised_date: datetime
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
