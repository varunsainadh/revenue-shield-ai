from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.recovery_case_model import RecoveryCaseModel
from app.schemas.recovery import RecoveryCaseResponse, RecoveryCaseCreate
from app.services.recovery_service import RecoveryService

router = APIRouter()

@router.get("/cases", response_model=List[RecoveryCaseResponse])
def list_cases(
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    failure_reason: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(RecoveryCaseModel)
    if status:
        query = query.filter(RecoveryCaseModel.status == status)
    if channel:
        query = query.filter(RecoveryCaseModel.recommended_channel == channel)
    if failure_reason:
        query = query.filter(RecoveryCaseModel.failure_reason == failure_reason)
    if risk_level:
        query = query.filter(RecoveryCaseModel.risk_level == risk_level)

    cases = query.order_by(RecoveryCaseModel.created_at.desc()).limit(limit).all()
    return cases

@router.get("/cases/{case_id}", response_model=RecoveryCaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case

@router.post("/cases", response_model=RecoveryCaseResponse)
def create_case(payload: RecoveryCaseCreate, db: Session = Depends(get_db)):
    service = RecoveryService(db)
    return service.create_case(payload.model_dump())
