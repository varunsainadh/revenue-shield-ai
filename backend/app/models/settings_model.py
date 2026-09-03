from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.database import Base

class SettingsModel(Base):
    __tablename__ = "merchant_settings"

    id = Column(Integer, primary_key=True, default=1)
    auto_recovery_enabled = Column(Boolean, default=True)
    max_attempts = Column(Integer, default=3)
    recovery_window_hours = Column(Integer, default=72)
    high_value_threshold = Column(Float, default=15000.0)
    quiet_hours_start = Column(Integer, default=21)
    quiet_hours_end = Column(Integer, default=9)
    voice_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    merchant_timezone = Column(String, default="Asia/Kolkata")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
