from pydantic import BaseModel, ConfigDict
from typing import Optional

class MerchantSettingsSchema(BaseModel):
    auto_recovery_enabled: bool = True
    max_attempts: int = 3
    recovery_window_hours: int = 72
    high_value_threshold: float = 15000.0
    quiet_hours_start: int = 21
    quiet_hours_end: int = 9
    voice_enabled: bool = True
    whatsapp_enabled: bool = True
    email_enabled: bool = True
    merchant_timezone: str = "Asia/Kolkata"

    model_config = ConfigDict(from_attributes=True)
