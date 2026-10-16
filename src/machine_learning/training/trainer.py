from pathlib import Path
import joblib


def train_model(model, X_train, y_train, model_path=None):
    """Fit a scikit-learn compatible estimator and optionally save it."""
    model.fit(X_train, y_train)

    saved_path = None
    if model_path is not None:
        path = Path(model_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        saved_path = str(path.resolve())

    return {"model": model, "model_path": saved_path}


def load_model(model_path):
    """Load a trusted model file created by this project."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)
