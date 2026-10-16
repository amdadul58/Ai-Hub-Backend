from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def make_kmeans(n_clusters=3, **kwargs):
    """Create a numeric preprocessing and KMeans clustering pipeline."""
    kwargs.setdefault("random_state", 42)
    kwargs.setdefault("n_init", 10)

    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", KMeans(n_clusters=n_clusters, **kwargs)),
    ])
