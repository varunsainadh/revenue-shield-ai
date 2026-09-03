from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings_model import SettingsModel
from app.schemas.settings import MerchantSettingsSchema

router = APIRouter()

@router.get("/settings", response_model=MerchantSettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    s = db.query(SettingsModel).filter(SettingsModel.id == 1).first()
    if not s:
        s = SettingsModel()
        db.add(s)
        db.commit()
        db.refresh(s)
    return s

@router.put("/settings", response_model=MerchantSettingsSchema)
def update_settings(payload: MerchantSettingsSchema, db: Session = Depends(get_db)):
    s = db.query(SettingsModel).filter(SettingsModel.id == 1).first()
    if not s:
        s = SettingsModel(id=1)
        db.add(s)

    for field, val in payload.model_dump().items():
        setattr(s, field, val)

    db.commit()
    db.refresh(s)
    return s
