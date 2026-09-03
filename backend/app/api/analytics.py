from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import MetricsSummary, AnalyticsData
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/metrics", response_model=MetricsSummary)
def get_metrics(db: Session = Depends(get_db)):
    return AnalyticsService.get_metrics_summary(db)

@router.get("/analytics", response_model=AnalyticsData)
def get_analytics(db: Session = Depends(get_db)):
    return AnalyticsService.get_analytics_data(db)
