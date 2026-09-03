from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class MetricsSummary(BaseModel):
    total_transactions: int
    failed_transactions: int
    revenue_at_risk: float
    recovered_revenue: float
    net_recovered_revenue: float
    recovery_rate: float
    recovery_efficiency: float
    active_recovery_cases: int
    recovered_cases: int
    manual_reviews: int
    blocked_cases: int
    top_performing_channel: str

class AuditLogResponse(BaseModel):
    id: str
    case_id: Optional[str] = None
    timestamp: datetime
    event_type: str
    actor: str
    action: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: Optional[str] = None
    confidence: Optional[float] = None
    policy_rule: Optional[str] = None
    metadata_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AnalyticsData(BaseModel):
    metrics: MetricsSummary
    revenue_trend: List[Dict[str, Any]]
    funnel: List[Dict[str, Any]]
    channel_performance: List[Dict[str, Any]]
    failure_reasons: List[Dict[str, Any]]
