
from fastapi import APIRouter, Query, HTTPException

from src.services.dashboard_service import (
    get_dashboard_summary,
    get_usage_analytics,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary():
    return get_dashboard_summary()


@router.get("/analytics")
def dashboard_analytics(
    days: int = Query(default=7, description="Supported values: 7, 30, 90"),
):
    if days not in (7, 30, 90):
        raise HTTPException(
            status_code=400,
            detail="days must be 7, 30, or 90",
        )

    return get_usage_analytics(days)
