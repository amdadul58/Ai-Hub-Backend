from pathlib import Path

import numpy as np
from fastapi import APIRouter, HTTPException

from src.schemas.machine_learning import (
    TrainRequest,
    PredictRequest,
    TrainResponse,
    PredictResponse,
)
from src.machine_learning.algorithms.classification import make_classifier
from src.machine_learning.algorithms.regression import make_regressor
from src.machine_learning.evaluation.metrics import (
    classification_metrics,
    regression_metrics,
)
from src.machine_learning.training.trainer import train_model, load_model
from src.machine_learning.inference.predictor import predict

router = APIRouter(prefix="/machine-learning", tags=["Machine Learning"])

MODEL_DIR = Path("artifacts") / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/algorithms")
def list_algorithms():
    return {
        "classification": [
            "logistic_regression",
            "decision_tree",
            "random_forest",
        ],
        "regression": [
            "linear_regression",
            "ridge",
            "decision_tree",
            "random_forest",
        ],
    }


@router.get("/metrics")
def list_metrics():
    return {
        "classification": [
            "accuracy",
            "precision_weighted",
            "recall_weighted",
            "f1_weighted",
        ],
        "regression": ["mae", "mse", "rmse", "r2"],
    }


@router.post("/train", response_model=TrainResponse)
def train_endpoint(request: TrainRequest):
    if len(request.features) != len(request.targets):
        raise HTTPException(
            status_code=400,
            detail="Number of feature rows must match number of targets.",
        )

    X = np.asarray(request.features, dtype=float)
    y = np.asarray(request.targets)

    if X.ndim != 2 or X.shape[1] == 0:
        raise HTTPException(status_code=400, detail="Features must be a non-empty 2D array.")
    if not np.isfinite(X).all():
        raise HTTPException(status_code=400, detail="Features must contain finite numeric values.")

    if request.task == "classification":
        if len(np.unique(y)) < 2:
            raise HTTPException(status_code=400, detail="Classification requires at least two target classes.")
        if request.algorithm not in {"logistic_regression", "decision_tree", "random_forest"}:
            raise HTTPException(status_code=400, detail="Selected algorithm is not a classifier.")
        model = make_classifier(request.algorithm)
    else:
        if request.algorithm not in {"linear_regression", "ridge", "decision_tree", "random_forest"}:
            raise HTTPException(status_code=400, detail="Selected algorithm is not a regressor.")
        y = y.astype(float)
        if not np.isfinite(y).all():
            raise HTTPException(status_code=400, detail="Targets must contain finite numeric values.")
        model = make_regressor(request.algorithm)

    model_path = MODEL_DIR / request.model_name

    try:
        result = train_model(model, X, y, model_path)
        y_pred = predict(result["model"], X)
        if request.task == "classification":
            metrics = classification_metrics(y, y_pred)
        else:
            metrics = regression_metrics(y, y_pred)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TrainResponse(
        status="trained",
        task=request.task,
        algorithm=request.algorithm,
        model_name=request.model_name,
        metrics=metrics,
    )


@router.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    model_path = MODEL_DIR / request.model_name

    try:
        model = load_model(model_path)
        X = np.asarray(request.features, dtype=float)
        if X.ndim != 2 or X.shape[1] == 0 or not np.isfinite(X).all():
            raise HTTPException(status_code=400, detail="Features must be a finite, non-empty 2D array.")
        predictions = predict(model, X)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Saved model not found.") from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictResponse(
        model_name=request.model_name,
        predictions=predictions,
    )
