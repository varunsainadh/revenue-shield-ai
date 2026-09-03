from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.refund_model import RefundModel
from app.schemas.refund import RefundResponse, RefundCreateRequest
from app.services.razorpay_service import RazorpayService

router = APIRouter()

@router.get("/refunds", response_model=List[RefundResponse])
def list_refunds(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    service = RazorpayService(db)
    return service.list_refunds(limit=limit)

@router.post("/razorpay/refund", response_model=RefundResponse)
def trigger_refund(payload: RefundCreateRequest, db: Session = Depends(get_db)):
    service = RazorpayService(db)
    return service.process_refund(
        payment_id=payload.payment_id,
        amount=payload.amount,
        reason=payload.reason or "Merchant initiated refund"
    )
