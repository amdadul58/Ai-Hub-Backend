from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from src.machine_learning.preprocessing.pipeline import make_numeric_pipeline


def make_regressor(algorithm="linear_regression", **kwargs):
    """Create a regression pipeline."""
    name = algorithm.strip().lower()

    if name == "linear_regression":
        estimator = LinearRegression(**kwargs)
    elif name == "ridge":
        estimator = Ridge(**kwargs)
    elif name == "decision_tree":
        estimator = DecisionTreeRegressor(random_state=42, **kwargs)
    elif name == "random_forest":
        estimator = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=1,
            **kwargs,
        )
    else:
        raise ValueError(
            "Unsupported regressor. Choose linear_regression, ridge, "
            "decision_tree, or random_forest."
        )

    return make_numeric_pipeline(estimator, scale=(name in {"linear_regression", "ridge"}))
