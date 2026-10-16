import pandas as pd
import pytest

from src.data_processing.cleaning import clean_dataframe
from src.data_processing.validation import (
    validate_dataframe,
    validate_numeric_values,
)
from src.data_processing.feature_engineering import (
    add_numeric_interaction,
    add_datetime_features,
)
from src.data_processing.splitting import split_dataset
from src.data_processing.transformation import (
    apply_column_mapping,
    fill_missing_values,
)


def test_clean_dataframe_strips_strings_and_drops_duplicates():
    df = pd.DataFrame({"name": [" Alice ", "Alice"], "score": [10, 10]})
    result = clean_dataframe(df)

    assert len(result) == 1
    assert result.iloc[0]["name"] == "Alice"
    assert len(df) == 2


def test_clean_dataframe_can_drop_empty_rows():
    df = pd.DataFrame({"a": [1, None], "b": [2, None]})
    result = clean_dataframe(df, drop_empty_rows=True)

    assert len(result) == 1


def test_validate_dataframe_reports_missing_columns_and_empty_data():
    df = pd.DataFrame(columns=["name"])
    errors = validate_dataframe(df, required_columns=["name", "age"])

    assert any("Missing required columns" in error for error in errors)
    assert "Dataset has no rows." in errors


def test_validate_numeric_values_handles_nan_and_infinity():
    assert validate_numeric_values([1, 2.5, "3"])
    assert not validate_numeric_values([1, float("inf")])
    assert not validate_numeric_values([1, float("nan")])
    assert validate_numeric_values([1, float("nan")], allow_nan=True)
    assert not validate_numeric_values([1, "not-a-number"])


def test_add_numeric_interaction_does_not_mutate_input():
    df = pd.DataFrame({"a": [2, 3], "b": [4, 5]})
    result = add_numeric_interaction(df, "a", "b")

    assert result["a_x_b"].tolist() == [8, 15]
    assert "a_x_b" not in df.columns


def test_add_numeric_interaction_rejects_missing_column():
    df = pd.DataFrame({"a": [1]})

    with pytest.raises(ValueError):
        add_numeric_interaction(df, "a", "missing")


def test_add_datetime_features_creates_date_columns():
    df = pd.DataFrame({"date": ["2026-10-15", "2025-01-02"]})
    result = add_datetime_features(df, "date")

    assert result["date_year"].tolist() == [2026, 2025]
    assert result["date_month"].tolist() == [10, 1]
    assert result["date_day"].tolist() == [15, 2]


def test_split_dataset_preserves_row_counts():
    X = list(range(20))
    y = [value % 2 for value in X]

    X_train, X_test, y_train, y_test = split_dataset(
        X, y, test_size=0.25, random_state=42
    )

    assert len(X_train) == 15
    assert len(X_test) == 5
    assert len(y_train) == 15
    assert len(y_test) == 5


def test_split_dataset_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        split_dataset([1, 2, 3], [0, 1])


def test_apply_column_mapping_renames_columns():
    df = pd.DataFrame({"old": [1, 2]})
    result = apply_column_mapping(df, {"old": "new"})

    assert result["new"].tolist() == [1, 2]
    assert "old" in df.columns


def test_apply_column_mapping_rejects_unknown_column():
    with pytest.raises(ValueError):
        apply_column_mapping(pd.DataFrame({"a": [1]}), {"missing": "new"})


def test_fill_missing_values_fills_numeric_and_text_columns():
    df = pd.DataFrame({
        "score": [1.0, None, 3.0],
        "city": ["Riyadh", None, "Jubail"],
    })
    result = fill_missing_values(df)

    assert result["score"].isna().sum() == 0
    assert result.loc[1, "score"] == 2.0
    assert result.loc[1, "city"] == "unknown"
    assert df["score"].isna().sum() == 1


def test_fill_missing_values_rejects_invalid_strategy():
    with pytest.raises(ValueError):
        fill_missing_values(pd.DataFrame({"x": [1]}), numeric_strategy="mode")
