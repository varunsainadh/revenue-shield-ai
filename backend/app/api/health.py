from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "app_mode": settings.APP_MODE,
        "use_razorpay": settings.USE_RAZORPAY,
        "use_gemini": settings.USE_GEMINI
    }
