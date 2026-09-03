from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.audit_model import AuditModel
from app.schemas.analytics import AuditLogResponse

router = APIRouter()

@router.get("/audit", response_model=List[AuditLogResponse])
def list_audit_logs(
    case_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(AuditModel)
    if case_id:
        query = query.filter(AuditModel.case_id == case_id)
    if event_type:
        query = query.filter(AuditModel.event_type == event_type)

    return query.order_by(AuditModel.timestamp.desc()).limit(limit).all()
