import os
import hmac
import hashlib
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.config import settings
from app.models.recovery_case_model import RecoveryCaseModel
from app.models.payment_link_model import PaymentLinkModel
from app.services.recovery_service import RecoveryService
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

router = APIRouter()

@router.post("/demo/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    from app.database import init_db
    init_db()
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "data", "transactions.csv")
    if not os.path.exists(csv_path):
        from scripts.generate_dataset import generate_dataset
        generate_dataset(num_records=1000)

    df = pd.read_csv(csv_path)
    rec_service = RecoveryService(db)

    seeded_count = 0
    # Seed top 100 cases from dataset into DB for fast interactive demo
    for _, row in df.head(150).iterrows():
        existing = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.transaction_id == str(row["transaction_id"])).first()
        if not existing:
            rec_service.create_case({
                "transaction_id": str(row["transaction_id"]),
                "customer_id": str(row["customer_id"]),
                "amount": float(row["amount"]),
                "currency": str(row["currency"]),
                "payment_method": str(row["payment_method"]),
                "bank": str(row["bank"]),
                "failure_reason": str(row["failure_reason"]),
                "hour_of_day": int(row["hour_of_day"]),
                "day_of_week": int(row["day_of_week"]),
                "previous_success_count": int(row["previous_success_count"]),
                "previous_failure_count": int(row["previous_failure_count"]),
                "customer_success_rate": float(row["customer_success_rate"]),
                "gateway_latency_ms": int(row["gateway_latency_ms"]),
                "device_type": str(row["device_type"]),
                "risk_level": str(row["risk_level"])
            })
            seeded_count += 1

    # Ensure Specific Demo Scenarios exist
    demo_scenarios = [
        {"transaction_id": "tx_demo_scenario_1", "customer_id": "cust_101", "amount": 2499.0, "failure_reason": "incorrect_pin", "risk_level": "LOW"},
        {"transaction_id": "tx_demo_scenario_2", "customer_id": "cust_102", "amount": 899.0, "failure_reason": "bank_down", "risk_level": "LOW"},
        {"transaction_id": "tx_demo_scenario_3", "customer_id": "cust_103", "amount": 18999.0, "failure_reason": "authentication_failed", "risk_level": "LOW"},
        {"transaction_id": "tx_demo_scenario_4", "customer_id": "cust_104", "amount": 4999.0, "failure_reason": "fraud_suspected", "risk_level": "HIGH"},
    ]

    for sc in demo_scenarios:
        existing = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.transaction_id == sc["transaction_id"]).first()
        if not existing:
            rec_service.create_case({
                "transaction_id": sc["transaction_id"],
                "customer_id": sc["customer_id"],
                "amount": sc["amount"],
                "currency": "INR",
                "payment_method": "UPI",
                "bank": "HDFC",
                "failure_reason": sc["failure_reason"],
                "risk_level": sc["risk_level"]
            })
            seeded_count += 1

    return {"status": "success", "message": f"Seeded {seeded_count} payment failure records into SQLite database."}

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    body_bytes = await request.body()
    
    # Signature verification if Razorpay secret is set
    if settings.USE_RAZORPAY and settings.RAZORPAY_WEBHOOK_SECRET:
        if not x_razorpay_signature:
            AuditService.log_event(db, AuditEventType.WEBHOOK_REJECTED, "Webhook rejected: Missing signature header")
            raise HTTPException(status_code=400, detail="Missing Razorpay signature header")

        expected_sig = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
            body_bytes,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, x_razorpay_signature):
            AuditService.log_event(db, AuditEventType.WEBHOOK_REJECTED, "Webhook rejected: Invalid signature")
            raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event = payload.get("event")
    AuditService.log_event(db, AuditEventType.WEBHOOK_RECEIVED, f"Webhook received: {event}", metadata={"event": event})

    if event in ["payment_link.paid", "payment.captured"]:
        plink_entity = payload.get("payload", {}).get("payment_link", {}).get("entity", {}) or payload.get("payload", {}).get("payment", {}).get("entity", {})
        ref_id = plink_entity.get("reference_id") or plink_entity.get("notes", {}).get("case_id")

        if ref_id:
            # Locate case by ID or by PaymentLink model reference
            plink = db.query(PaymentLinkModel).filter(
                (PaymentLinkModel.invoice_reference == ref_id) | (PaymentLinkModel.bound_case_id == ref_id)
            ).first()

            target_case_id = plink.bound_case_id if plink else ref_id
            case = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == target_case_id).first()

            if case:
                rec_service = RecoveryService(db)
                rec_service.process_payment_success(case.id)
                if plink:
                    plink.status = "PAID"
                    db.commit()

    return {"status": "processed", "event": event}

@router.post("/demo/cases/{case_id}/payment-success")
@router.get("/demo/cases/{case_id}/payment-success")
def demo_payment_success(case_id: str, db: Session = Depends(get_db)):
    rec_service = RecoveryService(db)
    try:
        case = rec_service.process_payment_success(case_id)
        # Update payment link status to PAID
        plink = db.query(PaymentLinkModel).filter(PaymentLinkModel.bound_case_id == case_id).first()
        if plink:
            plink.status = "PAID"
            db.commit()
            
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Successful - RevenueShield AI Demo</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; text-align: center; max-width: 420px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
                .icon {{ background: #10b981; color: white; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px auto; }}
                h2 {{ margin: 0 0 8px 0; color: #f8fafc; }}
                p {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
                .badge {{ background: #064e3b; color: #34d399; padding: 6px 12px; border-radius: 9999px; font-weight: 600; font-size: 13px; display: inline-block; margin-bottom: 16px; }}
                .btn {{ background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; text-decoration: none; cursor: pointer; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icon">✓</div>
                <div class="badge">DEMO PAYMENT SUCCESS</div>
                <h2>₹{case.amount:,.2f} Recovered!</h2>
                <p>Case ID: {case.id}<br>Status updated to <strong>RECOVERED</strong> in RevenueShield AI.</p>
                <a href="javascript:window.close()" class="btn">Close Tab</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
