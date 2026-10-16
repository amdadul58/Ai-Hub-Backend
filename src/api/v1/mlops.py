from fastapi import APIRouter, HTTPException
from src.mlops.drift_detection import numeric_drift
from src.mlops.experiment_tracker import ExperimentTracker
from src.mlops.metrics import metrics_collector
from src.mlops.monitoring import model_monitor
from src.schemas.mlops import DriftRequest, ExperimentLogRequest

router = APIRouter(prefix="/mlops", tags=["MLOps"])
tracker = ExperimentTracker()


@router.get("/status")
def mlops_status():
    return {"module": "MLOps", "status": "available"}


@router.get("/metrics")
def get_metrics():
    return metrics_collector.snapshot()


@router.get("/monitoring")
def get_monitoring_summary():
    return model_monitor.summary()


@router.post("/drift")
def detect_drift(request: DriftRequest):
    try:
        return numeric_drift(request.reference, request.current, request.relative_threshold)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/experiments")
def log_experiment(request: ExperimentLogRequest):
    try:
        return tracker.log(request.experiment_name, request.parameters, request.metrics, request.tags)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/experiments")
def list_experiments(experiment_name: str | None = None):
    try:
        return {"runs": tracker.list_runs(experiment_name)}
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
