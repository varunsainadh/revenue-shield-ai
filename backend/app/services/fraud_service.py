import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.fraud_model import FraudAlertModel
from app.ml.fraud_detector import FraudDetector
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

class FraudService:
    def __init__(self, db: Session):
        self.db = db

    def check_and_create_refund_alerts(
        self,
        payment_id: str,
        customer_id: str,
        amount: float,
        recent_count: int = 0,
        is_dup: bool = False
    ) -> List[FraudAlertModel]:
        alerts_domain = FraudDetector.inspect_refund_event(payment_id, customer_id, amount, recent_count, is_dup)
        stored_alerts: List[FraudAlertModel] = []

        for ad in alerts_domain:
            entry = FraudAlertModel(
                transaction_id=ad.transaction_id,
                customer_id=ad.customer_id,
                alert_type=ad.alert_type.value,
                severity=ad.severity.value,
                description=ad.description,
                evidence_json=json.dumps(ad.evidence),
                status="OPEN"
            )
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            stored_alerts.append(entry)

            AuditService.log_event(
                db=self.db,
                event_type=AuditEventType.FRAUD_ALERT_GENERATED,
                action=f"Fraud alert generated: {ad.alert_type.value} ({ad.severity.value})",
                metadata={"alert_id": entry.id, "type": ad.alert_type.value, "severity": ad.severity.value}
            )

        return stored_alerts

    def list_alerts(self, status: Optional[str] = None, limit: int = 100) -> List[FraudAlertModel]:
        query = self.db.query(FraudAlertModel)
        if status:
            query = query.filter(FraudAlertModel.status == status)
        return query.order_by(FraudAlertModel.created_at.desc()).limit(limit).all()

    def resolve_alert(self, alert_id: str, status: str = "RESOLVED", notes: str = "Resolved by merchant") -> FraudAlertModel:
        alert = self.db.query(FraudAlertModel).filter(FraudAlertModel.id == alert_id).first()
        if not alert:
            raise ValueError(f"Fraud alert {alert_id} not found")

        alert.status = status
        self.db.commit()
        self.db.refresh(alert)

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.FRAUD_ALERT_RESOLVED,
            action=f"Fraud alert {alert_id} marked as {status}",
            reason=notes
        )

        return alert
