from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def make_numeric_pipeline(estimator, scale=True):
    """Build a numeric preprocessing and estimator pipeline."""
    steps = [("imputer", SimpleImputer(strategy="median"))]

    if scale:
        steps.append(("scaler", StandardScaler()))

    steps.append(("model", estimator))
    return Pipeline(steps)
