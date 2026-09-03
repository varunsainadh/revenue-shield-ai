from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.chargeback_model import ChargebackPredictionModel
from app.schemas.chargeback import ChargebackPredictionResponse, ChargebackPredictRequest
from app.services.chargeback_service import ChargebackService

router = APIRouter()

@router.get("/chargebacks", response_model=List[ChargebackPredictionResponse])
def list_chargebacks(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    service = ChargebackService(db)
    return service.list_predictions(limit=limit)

@router.get("/chargebacks/{chargeback_id}", response_model=ChargebackPredictionResponse)
def get_chargeback(chargeback_id: str, db: Session = Depends(get_db)):
    entry = db.query(ChargebackPredictionModel).filter(ChargebackPredictionModel.id == chargeback_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Chargeback prediction {chargeback_id} not found")
    return entry

@router.post("/chargebacks/predict", response_model=ChargebackPredictionResponse)
def predict_chargeback_risk(payload: ChargebackPredictRequest, db: Session = Depends(get_db)):
    service = ChargebackService(db)
    return service.predict_and_store(payload.model_dump())
