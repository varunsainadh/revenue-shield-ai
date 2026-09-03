import pytest
from app.database import init_db, SessionLocal
from app.ml.chargeback_model import ChargebackPredictor
from app.ml.fraud_detector import FraudDetector
from app.services.chargeback_service import ChargebackService
from app.services.fraud_service import FraudService
from app.services.copilot_service import CopilotService
from app.services.razorpay_service import RazorpayService

def test_chargeback_risk_predictor_xai():
    res = ChargebackPredictor.predict_risk({
        "transaction_id": "tx_test_cb_1",
        "customer_id": "cust_new_1",
        "amount": 24999.0,
        "is_first_time_customer": True,
        "previous_failure_count": 3,
        "failure_reason": "fraud_suspected",
        "risk_level": "HIGH"
    })
    assert res.risk_score >= 80
    assert len(res.top_risk_factors) >= 3
    factor_names = [f.factor for f in res.top_risk_factors]
    assert "First-time Customer" in factor_names
    assert "High Transaction Value" in factor_names

def test_fraud_detector_anomaly_rules():
    alerts = FraudDetector.inspect_refund_event(
        payment_id="pay_test_dup_1",
        customer_id="cust_abuser_1",
        amount=5000.0,
        recent_refunds_count=4,
        is_duplicate=True
    )
    assert len(alerts) == 2
    types = [a.alert_type.value for a in alerts]
    assert "DUPLICATE_REFUND" in types
    assert "REFUND_ABUSE" in types

def test_copilot_service_query():
    init_db()
    db = SessionLocal()
    try:
        copilot_svc = CopilotService(db)
        resp = copilot_svc.query("Why did revenue decrease?")
        assert "answer" in resp
        assert "insights" in resp
        assert len(resp["insights"]) > 0
        assert "Revenue" in resp["answer"] or "failed" in resp["answer"]
    finally:
        db.close()

def test_razorpay_refund_and_fraud_alert_creation():
    init_db()
    db = SessionLocal()
    try:
        rzp_svc = RazorpayService(db)
        ref1 = rzp_svc.process_refund("pay_test_rf_1", 2000.0, "Initial refund")
        assert ref1.id is not None
        
        # Duplicate refund
        ref2 = rzp_svc.process_refund("pay_test_rf_1", 2000.0, "Duplicate attempt")
        assert ref2.is_suspicious is True
        
        fraud_svc = FraudService(db)
        alerts = fraud_svc.list_alerts(status="OPEN")
        assert len(alerts) > 0
    finally:
        db.close()
