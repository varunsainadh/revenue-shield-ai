from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
from app.models.payment_link_model import PaymentLinkModel
from app.models.recovery_case_model import RecoveryCaseModel
from app.config import settings

class PaymentLinkService:
    @staticmethod
    def get_or_create_payment_link(db: Session, case: RecoveryCaseModel) -> PaymentLinkModel:
        # Check idempotency: check if active link exists for case
        existing_link = (
            db.query(PaymentLinkModel)
            .filter(PaymentLinkModel.bound_case_id == case.id, PaymentLinkModel.status == "CREATED")
            .first()
        )
        if existing_link:
            return existing_link

        invoice_ref = f"inv_{case.id}_{uuid.uuid4().hex[:6]}"
        expires_at = datetime.utcnow() + timedelta(hours=72)

        if settings.USE_RAZORPAY and settings.RAZORPAY_KEY_ID and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_mock"):
            # Razorpay Test Mode Adapter
            try:
                import razorpay
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                resp = client.payment_link.create({
                    "amount": int(case.amount * 100),
                    "currency": case.currency or "INR",
                    "accept_partial": False,
                    "reference_id": invoice_ref,
                    "description": f"Payment recovery for case {case.id}",
                    "customer": {
                        "name": f"Customer {case.customer_id}",
                        "email": case.customer_email or "customer@example.com",
                        "contact": case.customer_phone or "+919876543210"
                    },
                    "notify": {"sms": False, "email": False},
                    "reminder_enable": False,
                    "callback_url": f"http://localhost:8000/api/demo/cases/{case.id}/payment-success",
                    "callback_method": "get"
                })
                rzp_id = resp.get("id")
                link_url = resp.get("short_url") or resp.get("url")
            except Exception:
                # Fallback to mock demo payment link
                rzp_id = f"plink_rzp_mock_{uuid.uuid4().hex[:8]}"
                link_url = f"/demo/pay/{case.id}"
        else:
            # Internal Demo / Mock Payment Link
            rzp_id = f"plink_rzp_mock_{uuid.uuid4().hex[:8]}"
            link_url = f"/demo/pay/{case.id}"

        link_model = PaymentLinkModel(
            bound_case_id=case.id,
            invoice_reference=invoice_ref,
            amount=case.amount,
            currency=case.currency or "INR",
            razorpay_link_id=rzp_id,
            url=link_url,
            status="CREATED",
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )

        db.add(link_model)
        db.commit()
        db.refresh(link_model)
        return link_model
