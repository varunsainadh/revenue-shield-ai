import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RevenueShield AI"
    APP_MODE: str = "mock"  # mock, test, production
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "sqlite:///./revenueshield.db"

    USE_RAZORPAY: bool = False
    USE_GEMINI: bool = False
    USE_EMAIL: bool = False
    USE_TWILIO: bool = False

    RAZORPAY_KEY_ID: Optional[str] = "rzp_test_mockkey12345"
    RAZORPAY_KEY_SECRET: Optional[str] = "mocksecret12345"
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = "mockwebhooksecret12345"

    GEMINI_API_KEY: Optional[str] = ""

    MERCHANT_TIMEZONE: str = "Asia/Kolkata"
    HIGH_VALUE_THRESHOLD: float = 15000.0
    MAX_RECOVERY_ATTEMPTS: int = 3
    MAX_RECOVERY_WINDOW_HOURS: int = 72

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
