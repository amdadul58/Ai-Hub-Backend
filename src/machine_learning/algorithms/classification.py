from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from src.machine_learning.preprocessing.pipeline import make_numeric_pipeline


def make_classifier(algorithm="logistic_regression", **kwargs):
    """Create a classification pipeline."""
    name = algorithm.strip().lower()

    if name == "logistic_regression":
        estimator = LogisticRegression(max_iter=1000, **kwargs)
    elif name == "decision_tree":
        estimator = DecisionTreeClassifier(random_state=42, **kwargs)
    elif name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=1,
            **kwargs,
        )
    else:
        raise ValueError(
            "Unsupported classifier. Choose logistic_regression, "
            "decision_tree, or random_forest."
        )

    return make_numeric_pipeline(estimator, scale=(name == "logistic_regression"))
