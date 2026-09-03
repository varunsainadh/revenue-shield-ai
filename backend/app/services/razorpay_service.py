import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.config import settings
from app.models.refund_model import RefundModel
from app.services.fraud_service import FraudService
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

class RazorpayService:
    def __init__(self, db: Session):
        self.db = db

    def process_refund(self, payment_id: str, amount: float, reason: str = "Customer request") -> RefundModel:
        # Check for duplicate refunds
        existing_dup = (
            self.db.query(RefundModel)
            .filter(RefundModel.payment_id == payment_id, RefundModel.amount == amount)
            .first()
        )
        is_suspicious = existing_dup is not None

        if settings.USE_RAZORPAY and settings.RAZORPAY_KEY_ID and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_mock"):
            try:
                import razorpay
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                resp = client.payment.refund(payment_id, {
                    "amount": int(amount * 100),
                    "notes": {"reason": reason}
                })
                ref_id = resp.get("id")
            except Exception:
                ref_id = f"rf_rzp_mock_{uuid.uuid4().hex[:8]}"
        else:
            ref_id = f"rf_rzp_mock_{uuid.uuid4().hex[:8]}"

        refund_entry = RefundModel(
            id=ref_id,
            payment_id=payment_id,
            customer_id="cust_101",
            amount=amount,
            currency="INR",
            status="PROCESSED",
            reason=reason,
            is_suspicious=is_suspicious
        )

        self.db.add(refund_entry)
        self.db.commit()
        self.db.refresh(refund_entry)

        # Trigger Fraud Detector check
        fraud_svc = FraudService(self.db)
        recent_cnt = self.db.query(RefundModel).filter(RefundModel.customer_id == "cust_101").count()
        fraud_svc.check_and_create_refund_alerts(
            payment_id=payment_id,
            customer_id="cust_101",
            amount=amount,
            recent_count=recent_cnt,
            is_dup=is_suspicious
        )

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.REFUND_TRIGGERED,
            action=f"Refund processed for ₹{amount:,.2f} on payment {payment_id}",
            metadata={"payment_id": payment_id, "amount": amount, "is_suspicious": is_suspicious}
        )

        return refund_entry

    def list_refunds(self, limit: int = 100) -> List[RefundModel]:
        return self.db.query(RefundModel).order_by(RefundModel.created_at.desc()).limit(limit).all()
