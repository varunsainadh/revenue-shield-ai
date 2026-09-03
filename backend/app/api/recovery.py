from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.recovery_case_model import RecoveryCaseModel
from app.schemas.recovery import RecoveryCaseResponse
from app.services.recovery_service import RecoveryService

router = APIRouter()

@router.post("/cases/{case_id}/analyze", response_model=RecoveryCaseResponse)
def analyze_case(case_id: str, db: Session = Depends(get_db)):
    service = RecoveryService(db)
    try:
        return service.analyze_case(case_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{case_id}/recover")
def execute_recovery(case_id: str, db: Session = Depends(get_db)):
    service = RecoveryService(db)
    try:
        return service.execute_recovery(case_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{case_id}/approve", response_model=RecoveryCaseResponse)
def approve_case(case_id: str, db: Session = Depends(get_db)):
    service = RecoveryService(db)
    try:
        return service.manual_approve(case_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{case_id}/reject", response_model=RecoveryCaseResponse)
def reject_case(
    case_id: str,
    reason: Optional[str] = Body(default="Rejected by merchant operator"),
    db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    try:
        return service.manual_reject(case_id, reason=reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{case_id}/stop", response_model=RecoveryCaseResponse)
def stop_case(
    case_id: str,
    reason: Optional[str] = Body(default="Recovery manually stopped by merchant"),
    db: Session = Depends(get_db)
):
    service = RecoveryService(db)
    try:
        return service.manual_reject(case_id, reason=reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/manual-review", response_model=List[RecoveryCaseResponse])
def get_manual_reviews(db: Session = Depends(get_db)):
    return (
        db.query(RecoveryCaseModel)
        .filter(RecoveryCaseModel.status == "MANUAL_REVIEW")
        .order_by(RecoveryCaseModel.created_at.desc())
        .all()
    )
