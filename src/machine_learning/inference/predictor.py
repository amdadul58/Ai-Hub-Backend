import numpy as np
from src.machine_learning.training.trainer import load_model


def predict(model, features):
    """Predict from an already loaded estimator and return JSON-friendly values."""
    predictions = model.predict(features)
    return np.asarray(predictions).tolist()


def predict_from_file(model_path, features):
    """Load a saved model and return predictions."""
    model = load_model(model_path)
    return predict(model, features)
