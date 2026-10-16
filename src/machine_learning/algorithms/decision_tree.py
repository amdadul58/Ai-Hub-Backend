from sklearn.tree import DecisionTreeClassifier
from src.machine_learning.preprocessing.pipeline import make_numeric_pipeline


def make_decision_tree_classifier(**kwargs):
    """Create a CPU-friendly decision tree classifier."""
    kwargs.setdefault("random_state", 42)
    return make_numeric_pipeline(DecisionTreeClassifier(**kwargs), scale=False)
