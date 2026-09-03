import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.chargeback_model import ChargebackPredictionModel
from app.ml.chargeback_model import ChargebackPredictor
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

class ChargebackService:
    def __init__(self, db: Session):
        self.db = db

    def predict_and_store(self, tx_data: Dict[str, Any]) -> ChargebackPredictionModel:
        tx_id = str(tx_data.get("transaction_id", "tx_unknown"))
        
        existing = self.db.query(ChargebackPredictionModel).filter(ChargebackPredictionModel.transaction_id == tx_id).first()
        if existing:
            return existing

        domain_pred = ChargebackPredictor.predict_risk(tx_data)

        factors_json = json.dumps([f.model_dump() for f in domain_pred.top_risk_factors])

        model_entry = ChargebackPredictionModel(
            transaction_id=domain_pred.transaction_id,
            customer_id=domain_pred.customer_id,
            amount=domain_pred.amount,
            risk_score=domain_pred.risk_score,
            risk_level=domain_pred.risk_level.value if hasattr(domain_pred.risk_level, 'value') else str(domain_pred.risk_level),
            confidence=domain_pred.confidence,
            top_risk_factors_json=factors_json,
            explanation=domain_pred.explanation
        )

        self.db.add(model_entry)
        self.db.commit()
        self.db.refresh(model_entry)

        # Audit Event
        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.CHARGEBACK_PREDICTED,
            action=f"Predicted Chargeback Risk Score of {model_entry.risk_score}% ({model_entry.risk_level})",
            metadata={"transaction_id": tx_id, "risk_score": model_entry.risk_score, "risk_level": model_entry.risk_level}
        )

        return model_entry

    def list_predictions(self, limit: int = 100) -> List[ChargebackPredictionModel]:
        return (
            self.db.query(ChargebackPredictionModel)
            .order_by(ChargebackPredictionModel.created_at.desc())
            .limit(limit)
            .all()
        )
