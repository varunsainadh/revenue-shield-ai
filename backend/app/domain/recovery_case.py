from typing import Optional, Dict, Any, List
from datetime import datetime
from app.domain.enums import CaseState, FailureReason, FailureCategory, RecoveryChannel, RecoveryActionType, RiskLevel

class InvalidStateTransitionError(Exception):
    def __init__(self, current_state: CaseState, target_state: CaseState):
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(f"Cannot transition RecoveryCase state from '{current_state.value}' to '{target_state.value}'")

def classify_failure_reason(reason: FailureReason | str) -> FailureCategory:
    if isinstance(reason, str):
        try:
            reason = FailureReason(reason)
        except ValueError:
            return FailureCategory.UNKNOWN
            
    mapping = {
        FailureReason.INCORRECT_PIN: FailureCategory.CUSTOMER_CORRECTABLE,
        FailureReason.AUTHENTICATION_FAILED: FailureCategory.CUSTOMER_CORRECTABLE,
        FailureReason.INSUFFICIENT_FUNDS: FailureCategory.INSUFFICIENT_FUNDS,
        FailureReason.BALANCE_LOW: FailureCategory.INSUFFICIENT_FUNDS,
        FailureReason.CARD_EXPIRED: FailureCategory.PAYMENT_METHOD_PROBLEM,
        FailureReason.BANK_DECLINED: FailureCategory.PAYMENT_METHOD_PROBLEM,
        FailureReason.PAYMENT_METHOD_UNAVAILABLE: FailureCategory.PAYMENT_METHOD_PROBLEM,
        FailureReason.BANK_DOWN: FailureCategory.TEMPORARY_INFRASTRUCTURE,
        FailureReason.GATEWAY_TIMEOUT: FailureCategory.TEMPORARY_INFRASTRUCTURE,
        FailureReason.NETWORK_ERROR: FailureCategory.TEMPORARY_INFRASTRUCTURE,
        FailureReason.CUSTOMER_CANCELLED: FailureCategory.CUSTOMER_ABANDONMENT,
        FailureReason.RISK_DECLINED: FailureCategory.RISK_RELATED,
        FailureReason.FRAUD_SUSPECTED: FailureCategory.RISK_RELATED,
        FailureReason.UNKNOWN: FailureCategory.UNKNOWN,
    }
    return mapping.get(reason, FailureCategory.UNKNOWN)

VALID_TRANSITIONS: Dict[CaseState, List[CaseState]] = {
    CaseState.OPEN: [CaseState.ANALYZING, CaseState.MANUAL_REVIEW, CaseState.STOPPED],
    CaseState.ANALYZING: [CaseState.ACTION_READY, CaseState.MANUAL_REVIEW, CaseState.STOPPED, CaseState.FAILED],
    CaseState.ACTION_READY: [CaseState.PENDING_RECOVERY, CaseState.WAITING_PAYMENT, CaseState.MANUAL_REVIEW, CaseState.STOPPED, CaseState.FAILED],
    CaseState.MANUAL_REVIEW: [CaseState.PENDING_RECOVERY, CaseState.ACTION_READY, CaseState.STOPPED, CaseState.FAILED],
    CaseState.PENDING_RECOVERY: [CaseState.WAITING_PAYMENT, CaseState.FAILED, CaseState.STOPPED, CaseState.RECOVERED],
    CaseState.WAITING_PAYMENT: [CaseState.RECOVERED, CaseState.FAILED, CaseState.STOPPED],
    CaseState.RECOVERED: [],
    CaseState.FAILED: [],
    CaseState.STOPPED: [],
}

def validate_state_transition(current_state: CaseState, target_state: CaseState) -> bool:
    if current_state == target_state:
        return True
    allowed = VALID_TRANSITIONS.get(current_state, [])
    if target_state not in allowed:
        raise InvalidStateTransitionError(current_state, target_state)
    return True
