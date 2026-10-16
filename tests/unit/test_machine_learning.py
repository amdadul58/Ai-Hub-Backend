import numpy as np
import pandas as pd
import pytest

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler

from src.machine_learning.preprocessing.encoder import (
    encode_labels,
    make_one_hot_encoder,
)
from src.machine_learning.preprocessing.scaler import (
    make_standard_scaler,
    make_minmax_scaler,
)
from src.machine_learning.preprocessing.pipeline import make_numeric_pipeline
from src.machine_learning.algorithms.classification import make_classifier
from src.machine_learning.algorithms.regression import make_regressor
from src.machine_learning.evaluation.metrics import (
    classification_metrics,
    regression_metrics,
)


@pytest.fixture
def classification_data():
    X = pd.DataFrame({
        "x1": [0, 1, 2, 3, 4, 5, 6, 7],
        "x2": [1, 0, 1, 0, 1, 0, 1, 0],
    })
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    return X, y


@pytest.fixture
def regression_data():
    X = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6]})
    y = np.array([3, 5, 7, 9, 11, 13])
    return X, y


def test_encode_labels_returns_encoder_and_encoded_values():
    result = encode_labels(["cat", "dog", "cat"])

    assert isinstance(result["encoder"], LabelEncoder)
    assert result["values"].tolist() == [0, 1, 0]


def test_one_hot_encoder_ignores_unknown_categories():
    encoder = make_one_hot_encoder()
    result = encoder.fit_transform([["red"], ["blue"]])
    unknown = encoder.transform([["green"]])

    assert isinstance(encoder, OneHotEncoder)
    assert result.shape == (2, 2)
    assert unknown.shape == (1, 2)


def test_scaler_factories_return_expected_scalers():
    assert isinstance(make_standard_scaler(), StandardScaler)
    assert isinstance(make_minmax_scaler(), MinMaxScaler)

    scaled = make_minmax_scaler().fit_transform([[0], [10]])
    assert np.allclose(scaled.ravel(), [0, 1])


def test_numeric_pipeline_imputes_missing_values(regression_data):
    X, y = regression_data
    X = X.copy()
    X.loc[1, "x"] = np.nan

    pipeline = make_numeric_pipeline(LinearRegression())
    pipeline.fit(X, y)
    predictions = pipeline.predict(X)

    assert len(predictions) == len(y)
    assert np.isfinite(predictions).all()


@pytest.mark.parametrize(
    "algorithm",
    ["logistic_regression", "decision_tree", "random_forest"],
)
def test_classifiers_fit_and_predict(classification_data, algorithm):
    X, y = classification_data
    model = make_classifier(algorithm)
    model.fit(X, y)

    predictions = model.predict(X)

    assert len(predictions) == len(y)
    assert set(predictions).issubset({0, 1})


def test_classifier_rejects_unknown_algorithm():
    with pytest.raises(ValueError):
        make_classifier("unsupported")


@pytest.mark.parametrize(
    "algorithm",
    ["linear_regression", "ridge", "decision_tree", "random_forest"],
)
def test_regressors_fit_and_predict(regression_data, algorithm):
    X, y = regression_data
    model = make_regressor(algorithm)
    model.fit(X, y)

    predictions = model.predict(X)

    assert len(predictions) == len(y)
    assert np.isfinite(predictions).all()


def test_regressor_rejects_unknown_algorithm():
    with pytest.raises(ValueError):
        make_regressor("unsupported")


def test_classification_metrics_return_expected_values():
    result = classification_metrics([0, 1, 1], [0, 1, 0])

    assert result["accuracy"] == pytest.approx(2 / 3)
    assert 0 <= result["precision_weighted"] <= 1
    assert 0 <= result["recall_weighted"] <= 1
    assert 0 <= result["f1_weighted"] <= 1


def test_regression_metrics_return_expected_values():
    result = regression_metrics([1, 2, 3], [1, 3, 2])

    assert result["mae"] == pytest.approx(2 / 3)
    assert result["mse"] == pytest.approx(2 / 3)
    assert result["rmse"] == pytest.approx((2 / 3) ** 0.5)
    assert result["r2"] == pytest.approx(0.0)
