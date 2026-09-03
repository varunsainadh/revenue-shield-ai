import os
import pytest
import pandas as pd
from app.ml.predictor import MLPredictor
from app.services.scoring_service import ScoringService
from app.services.recovery_service import RecoveryService
from app.database import init_db, SessionLocal
from app.models.recovery_case_model import RecoveryCaseModel
from app.models.audit_model import AuditModel
from app.domain.enums import CaseState, AuditEventType

def test_dataset_record_count_and_columns():
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "recovery_training_data.csv")
    assert os.path.exists(data_path)
    df = pd.read_csv(data_path)
    assert len(df) == 1000

    required_cols = [
        "transaction_id", "customer_id", "amount", "currency", "payment_method",
        "bank", "hour_of_day", "day_of_week", "failure_reason", "failure_category",
        "previous_success_count", "previous_failure_count", "customer_success_rate",
        "attempt_number", "gateway_latency_ms", "device_type", "risk_level",
        "email_recovery_success", "whatsapp_recovery_success", "voice_recovery_success",
        "recovered", "recovered_amount"
    ]
    for col in required_cols:
        assert col in df.columns

    # Verify binary targets
    for target in ["email_recovery_success", "whatsapp_recovery_success", "voice_recovery_success", "recovered"]:
        assert set(df[target].unique()).issubset({0, 1})

def test_ml_model_artifacts_exist():
    assert MLPredictor.is_trained() is True

def test_predictor_probability_bounds_and_erv():
    case_sample = {
        "amount": 2499.0,
        "currency": "INR",
        "payment_method": "UPI",
        "bank": "HDFC",
        "failure_reason": "incorrect_pin",
        "failure_category": "CUSTOMER_CORRECTABLE",
        "hour_of_day": 14,
        "day_of_week": 2,
        "previous_success_count": 5,
        "previous_failure_count": 1,
        "customer_success_rate": 0.833,
        "attempt_number": 1,
        "gateway_latency_ms": 250,
        "device_type": "mobile_android",
        "risk_level": "LOW"
    }

    res = ScoringService.get_predictions(case_sample)
    assert "channel_scores" in res
    assert "recoverability_score" in res
    assert 0.0 <= res["recoverability_score"] <= 1.0

    scores = res["channel_scores"]
    for ch in ["email", "whatsapp", "voice"]:
        assert ch in scores
        p = scores[ch]["probability"]
        erv = scores[ch]["erv"]
        assert 0.0 <= p <= 1.0
        # ERV formula check: P * Amount
        assert abs(erv - round(p * 2499.0, 2)) < 0.05

def test_erv_scaling_with_amount():
    case_low = {
        "amount": 1000.0,
        "failure_reason": "incorrect_pin",
        "customer_success_rate": 0.8,
        "risk_level": "LOW"
    }
    case_high = {
        "amount": 10000.0,
        "failure_reason": "incorrect_pin",
        "customer_success_rate": 0.8,
        "risk_level": "LOW"
    }

    res_low = ScoringService.get_predictions(case_low)
    res_high = ScoringService.get_predictions(case_high)

    wa_erv_low = res_low["channel_scores"]["whatsapp"]["erv"]
    wa_erv_high = res_high["channel_scores"]["whatsapp"]["erv"]

    assert wa_erv_high > wa_erv_low

def test_api_case_analysis_endpoint():
    import uuid
    init_db()
    db = SessionLocal()
    try:
        rec_service = RecoveryService(db)
        case = rec_service.create_case({
            "transaction_id": f"tx_test_ml_analyze_{uuid.uuid4().hex[:6]}",
            "customer_id": "cust_test_1",
            "amount": 2499.0,
            "failure_reason": "incorrect_pin",
            "risk_level": "LOW"
        })

        analyzed_case = rec_service.analyze_case(case.id)
        assert analyzed_case.status in [CaseState.ACTION_READY.value, CaseState.MANUAL_REVIEW.value, CaseState.STOPPED.value]
        assert analyzed_case.recommended_channel in ["EMAIL", "WHATSAPP", "VOICE"]
        assert analyzed_case.recommended_erv is not None
        assert analyzed_case.recoverability_score is not None

        # Verify Audit Logs for ML Events
        logs = db.query(AuditModel).filter(AuditModel.case_id == case.id).all()
        event_types = [l.event_type for l in logs]
        assert AuditEventType.ML_SCORING_STARTED.value in event_types
        assert AuditEventType.ML_SCORE_GENERATED.value in event_types
        assert AuditEventType.ERV_CALCULATED.value in event_types
        assert AuditEventType.CHANNEL_RECOMMENDED.value in event_types
    finally:
        db.close()
