import pytest
from datetime import datetime, timedelta
from app.domain.enums import CaseState, PTPStatus, FailureReason, RecoveryChannel, PolicyResult
from app.domain.recovery_case import validate_state_transition, InvalidStateTransitionError, classify_failure_reason
from app.domain.promise_to_pay import validate_ptp_transition, InvalidPTPTransitionError
from app.agents.guardrails import HighValueApprovalPolicy, FraudRiskPolicy, MaximumAttemptsPolicy, ActivePromiseToPayPolicy
from app.agents.deterministic_reasoner import DeterministicReasoner
from app.services.policy_service import PolicyService

def test_valid_case_state_transitions():
    assert validate_state_transition(CaseState.OPEN, CaseState.ANALYZING) is True
    assert validate_state_transition(CaseState.ANALYZING, CaseState.ACTION_READY) is True
    assert validate_state_transition(CaseState.ACTION_READY, CaseState.PENDING_RECOVERY) is True
    assert validate_state_transition(CaseState.PENDING_RECOVERY, CaseState.WAITING_PAYMENT) is True
    assert validate_state_transition(CaseState.WAITING_PAYMENT, CaseState.RECOVERED) is True

def test_invalid_case_state_transitions():
    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(CaseState.OPEN, CaseState.RECOVERED)

    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(CaseState.RECOVERED, CaseState.OPEN)

def test_ptp_state_transitions():
    assert validate_ptp_transition(PTPStatus.ACTIVE, PTPStatus.KEPT) is True
    with pytest.raises(InvalidPTPTransitionError):
        validate_ptp_transition(PTPStatus.KEPT, PTPStatus.ACTIVE)

def test_high_value_policy():
    decision = HighValueApprovalPolicy.evaluate(24999.0, threshold=15000.0)
    assert decision is not None
    assert decision.result == PolicyResult.MANUAL_REVIEW
    
    decision_low = HighValueApprovalPolicy.evaluate(2499.0, threshold=15000.0)
    assert decision_low is None

def test_fraud_risk_policy():
    decision = FraudRiskPolicy.evaluate("fraud_suspected", "HIGH")
    assert decision is not None
    assert decision.result == PolicyResult.BLOCK

def test_max_attempts_policy():
    decision = MaximumAttemptsPolicy.evaluate(3, max_attempts=3)
    assert decision is not None
    assert decision.result == PolicyResult.BLOCK

def test_deterministic_erv_scoring():
    res = DeterministicReasoner.evaluate({
        "amount": 2499.0,
        "failure_reason": "incorrect_pin",
        "customer_success_rate": 0.8,
        "risk_level": "LOW",
        "device_type": "mobile_android"
    })
    assert "channel_scores" in res
    assert "whatsapp" in res["channel_scores"]
    assert res["channel_scores"]["whatsapp"]["erv"] > 0
    assert res["recommended_channel"] in ["EMAIL", "WHATSAPP", "VOICE"]

def test_api_health():
    from fastapi.testclient import TestClient
    from app.database import init_db
    from app.main import app
    init_db()
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

def test_api_seed_and_cases():
    from fastapi.testclient import TestClient
    from app.database import init_db
    from app.main import app
    init_db()
    client = TestClient(app)
    
    seed_resp = client.post("/api/demo/seed")
    assert seed_resp.status_code == 200
    
    cases_resp = client.get("/api/cases")
    assert cases_resp.status_code == 200
    cases = cases_resp.json()
    assert len(cases) > 0
