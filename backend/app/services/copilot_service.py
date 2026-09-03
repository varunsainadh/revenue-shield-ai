from sqlalchemy.orm import Session
from typing import Dict, Any
from app.services.analytics_service import AnalyticsService
from app.agents.copilot_agent import CopilotAgent
from app.models.chargeback_model import ChargebackPredictionModel
from app.models.fraud_model import FraudAlertModel
from app.models.recovery_case_model import RecoveryCaseModel
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

class CopilotService:
    def __init__(self, db: Session):
        self.db = db

    def query(self, user_query: str) -> Dict[str, Any]:
        # 1. Retrieve RAG analytical context from database
        summary = AnalyticsService.get_metrics_summary(self.db)
        metrics_dict = summary.model_dump()

        high_risk_cb = (
            self.db.query(ChargebackPredictionModel)
            .filter(ChargebackPredictionModel.risk_score >= 60)
            .limit(10)
            .all()
        )
        high_risk_cases = [
            {"transaction_id": cb.transaction_id, "customer_id": cb.customer_id, "risk_score": cb.risk_score}
            for cb in high_risk_cb
        ]

        active_alerts = (
            self.db.query(FraudAlertModel)
            .filter(FraudAlertModel.status == "OPEN")
            .limit(10)
            .all()
        )
        alerts_list = [
            {"id": a.id, "alert_type": a.alert_type, "severity": a.severity, "description": a.description}
            for a in active_alerts
        ]

        recent_cases = (
            self.db.query(RecoveryCaseModel)
            .order_by(RecoveryCaseModel.created_at.desc())
            .limit(10)
            .all()
        )
        cases_list = [
            {"id": c.id, "amount": c.amount, "status": c.status, "failure_reason": c.failure_reason}
            for c in recent_cases
        ]

        context = {
            "metrics": metrics_dict,
            "high_risk_cases": high_risk_cases,
            "active_alerts": alerts_list,
            "recent_cases": cases_list
        }

        # 2. Invoke CopilotAgent processing
        response = CopilotAgent.answer_query(user_query, context)

        # 3. Log Audit Event
        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.COPILOT_QUERY_PROCESSED,
            action=f"AI Financial Copilot processed query: '{user_query}'",
            metadata={"query": user_query}
        )

        return response
