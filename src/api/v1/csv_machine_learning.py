from pathlib import Path
import io
import re

import joblib
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

from src.machine_learning.algorithms.classification import make_classifier
from src.machine_learning.algorithms.regression import make_regressor
from src.machine_learning.evaluation.metrics import (
    classification_metrics,
    regression_metrics,
)

router = APIRouter(
    prefix="/machine-learning/csv",
    tags=["Machine Learning - CSV"],
)

MODEL_DIR = Path("artifacts") / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MAX_CSV_BYTES = 10 * 1024 * 1024

CLASSIFIERS = {
    "logistic_regression",
    "decision_tree",
    "random_forest",
}
REGRESSORS = {
    "linear_regression",
    "ridge",
    "decision_tree",
    "random_forest",
}


def _validate_model_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise HTTPException(
            status_code=400,
            detail="model_name may contain only letters, numbers, dots, underscores and hyphens.",
        )
    if name in {".", ".."} or not name.lower().endswith(".joblib"):
        raise HTTPException(
            status_code=400,
            detail="model_name must be a safe filename ending in .joblib.",
        )
    return name


async def _read_csv(file: UploadFile) -> pd.DataFrame:
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file.")

    content = await file.read(MAX_CSV_BYTES + 1)
    if len(content) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV maximum size is 10 MB.")

    if not content.strip():
        raise HTTPException(status_code=400, detail="CSV file is empty.")

    try:
        frame = pd.read_csv(io.BytesIO(content))
    except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc
    finally:
        await file.close()

    if frame.empty or len(frame.columns) < 2:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain data rows and at least two columns.",
        )

    if not frame.columns.is_unique:
        raise HTTPException(status_code=400, detail="CSV column names must be unique.")

    frame.columns = [str(column).strip() for column in frame.columns]
    if any(not column for column in frame.columns):
        raise HTTPException(status_code=400, detail="CSV column names cannot be empty.")

    return frame


@router.post("/inspect")
async def inspect_csv(file: UploadFile = File(...)):
    """Inspect a CSV file without training a model."""
    frame = await _read_csv(file)
    columns = []

    for column in frame.columns:
        series = frame[column]
        columns.append({
            "name": column,
            "dtype": str(series.dtype),
            "missing_values": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=True)),
        })

    return {
        "filename": Path(file.filename or "dataset.csv").name,
        "rows": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": columns,
        "preview": frame.head(5).where(pd.notna(frame.head(5)), None).to_dict(orient="records"),
    }


@router.post("/train")
async def train_csv_model(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    task: str = Form(...),
    algorithm: str = Form(...),
    model_name: str = Form("csv_model.joblib"),
    test_size: float = Form(0.2),
):
    """Train and save a model using a CSV target column."""
    model_name = _validate_model_name(model_name)

    if task not in {"classification", "regression"}:
        raise HTTPException(status_code=400, detail="task must be classification or regression.")

    if not 0.1 <= test_size <= 0.4:
        raise HTTPException(status_code=400, detail="test_size must be between 0.1 and 0.4.")

    allowed = CLASSIFIERS if task == "classification" else REGRESSORS
    if algorithm not in allowed:
        raise HTTPException(status_code=400, detail=f"Algorithm is not valid for {task}.")

    frame = await _read_csv(file)

    if target_column not in frame.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Target column not found. Available columns: {list(frame.columns)}",
        )

    frame = frame.dropna(subset=[target_column]).copy()
    if len(frame) < 10:
        raise HTTPException(status_code=400, detail="At least 10 rows with a target value are required.")

    y = frame.pop(target_column)
    X = frame

    # Remove columns that contain no useful values.
    empty_columns = [column for column in X.columns if X[column].isna().all()]
    X = X.drop(columns=empty_columns)

    if X.empty:
        raise HTTPException(status_code=400, detail="No usable feature columns remain.")

    if task == "classification":
        if y.nunique() < 2:
            raise HTTPException(status_code=400, detail="Classification requires at least two classes.")
        if y.nunique() > 100:
            raise HTTPException(status_code=400, detail="Too many target classes for this endpoint.")
        if y.value_counts().min() < 2:
            raise HTTPException(
                status_code=400,
                detail="Each target class needs at least two rows for evaluation.",
            )
        y = y.astype(str)
        model = make_classifier(algorithm)
    else:
        y = pd.to_numeric(y, errors="coerce")
        valid_targets = y.notna()
        X = X.loc[valid_targets].copy()
        y = y.loc[valid_targets].astype(float)
        if len(y) < 10:
            raise HTTPException(status_code=400, detail="At least 10 numeric target values are required.")
        if not y.map(lambda value: abs(value) != float("inf")).all():
            raise HTTPException(status_code=400, detail="Target values must be finite.")
        model = make_regressor(algorithm)

    if len(X) < 10:
        raise HTTPException(status_code=400, detail="Not enough valid rows after target cleaning.")

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
            stratify=y if task == "classification" else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Could not split dataset: {exc}") from exc

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, make_column_selector(dtype_include="number")),
        ("categorical", categorical_pipeline, make_column_selector(dtype_exclude="number")),
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    try:
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        metrics = (
            classification_metrics(y_test, predictions)
            if task == "classification"
            else regression_metrics(y_test, predictions)
        )

        model_path = MODEL_DIR / model_name
        joblib.dump({
            "pipeline": pipeline,
            "feature_columns": list(X.columns),
            "target_column": target_column,
            "task": task,
            "algorithm": algorithm,
            "metrics": metrics,
        }, model_path)

    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=f"Training failed: {exc}") from exc

    return {
        "status": "trained",
        "task": task,
        "algorithm": algorithm,
        "model_name": model_name,
        "target_column": target_column,
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "feature_columns": list(X.columns),
        "dropped_empty_columns": empty_columns,
        "metrics": metrics,
    }


@router.post("/predict")
async def predict_csv_model(
    file: UploadFile = File(...),
    model_name: str = Form(...),
):
    """Predict rows in a CSV using a model trained by this CSV endpoint."""
    model_name = _validate_model_name(model_name)
    model_path = MODEL_DIR / model_name

    if not model_path.is_file():
        raise HTTPException(status_code=404, detail="CSV model not found.")

    try:
        bundle = joblib.load(model_path)
    except (OSError, ValueError, EOFError) as exc:
        raise HTTPException(status_code=500, detail="Could not load saved model.") from exc

    if not isinstance(bundle, dict) or "pipeline" not in bundle:
        raise HTTPException(
            status_code=400,
            detail="This model was not trained by the CSV training endpoint.",
        )

    frame = await _read_csv(file)
    feature_columns = bundle["feature_columns"]
    missing = [column for column in feature_columns if column not in frame.columns]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction CSV is missing feature columns: {missing}",
        )

    try:
        predictions = bundle["pipeline"].predict(frame[feature_columns]).tolist()
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {exc}") from exc

    return {
        "model_name": model_name,
        "row_count": len(predictions),
        "predictions": predictions,
    }
