from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse
from app.services.copilot_service import CopilotService

router = APIRouter()

@router.post("/copilot/chat", response_model=CopilotQueryResponse)
def copilot_chat(payload: CopilotQueryRequest, db: Session = Depends(get_db)):
    service = CopilotService(db)
    return service.query(payload.query)
