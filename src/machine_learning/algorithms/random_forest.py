from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from src.machine_learning.preprocessing.pipeline import make_numeric_pipeline


def make_random_forest_classifier(**kwargs):
    """Create a random forest classification pipeline."""
    kwargs.setdefault("n_estimators", 100)
    kwargs.setdefault("random_state", 42)
    kwargs.setdefault("n_jobs", 1)
    return make_numeric_pipeline(RandomForestClassifier(**kwargs), scale=False)


def make_random_forest_regressor(**kwargs):
    """Create a random forest regression pipeline."""
    kwargs.setdefault("n_estimators", 100)
    kwargs.setdefault("random_state", 42)
    kwargs.setdefault("n_jobs", 1)
    return make_numeric_pipeline(RandomForestRegressor(**kwargs), scale=False)
