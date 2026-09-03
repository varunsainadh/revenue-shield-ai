from typing import List, Dict
from datetime import datetime
from app.domain.enums import PTPStatus

class InvalidPTPTransitionError(Exception):
    def __init__(self, current_status: PTPStatus, target_status: PTPStatus):
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(f"Cannot transition PromiseToPay status from '{current_status.value}' to '{target_status.value}'")

VALID_PTP_TRANSITIONS: Dict[PTPStatus, List[PTPStatus]] = {
    PTPStatus.ACTIVE: [PTPStatus.KEPT, PTPStatus.BROKEN, PTPStatus.EXPIRED],
    PTPStatus.KEPT: [],
    PTPStatus.BROKEN: [],
    PTPStatus.EXPIRED: [],
}

def validate_ptp_transition(current_status: PTPStatus, target_status: PTPStatus) -> bool:
    if current_status == target_status:
        return True
    allowed = VALID_PTP_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        raise InvalidPTPTransitionError(current_status, target_status)
    return True
