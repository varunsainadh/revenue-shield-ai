from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.fraud_model import FraudAlertModel
from app.schemas.fraud import FraudAlertResponse, FraudAlertResolveRequest
from app.services.fraud_service import FraudService

router = APIRouter()

@router.get("/fraud/alerts", response_model=List[FraudAlertResponse])
def list_fraud_alerts(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    service = FraudService(db)
    return service.list_alerts(status=status, limit=limit)

@router.post("/fraud/alerts/{alert_id}/resolve", response_model=FraudAlertResponse)
def resolve_fraud_alert(
    alert_id: str,
    payload: FraudAlertResolveRequest,
    db: Session = Depends(get_db)
):
    service = FraudService(db)
    try:
        return service.resolve_alert(alert_id, status=payload.status, notes=payload.resolution_notes or "Handled by merchant operator")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
