from fastapi import APIRouter
from src.mlops.metrics import metrics_collector
from src.mlops.monitoring import model_monitor

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/status")
def monitoring_status():
    return {"module": "Monitoring", "status": "available"}


@router.get("/metrics")
def monitoring_metrics():
    return metrics_collector.snapshot()


@router.get("/models")
def monitoring_models():
    return model_monitor.summary()
