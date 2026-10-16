import math


def validate_dataframe(df, *, required_columns=None, allow_empty=False):
    """Validate a DataFrame's basic structure; return a list of errors."""
    errors = []
    required_columns = required_columns or []
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
    if not allow_empty and df.empty:
        errors.append("Dataset has no rows.")
    if len(df.columns) == 0:
        errors.append("Dataset has no columns.")
    return errors


def validate_numeric_values(values, *, allow_nan=False):
    """Return False if any value is non-numeric or infinite."""
    try:
        for value in values:
            number = float(value)
            if math.isinf(number) or (math.isnan(number) and not allow_nan):
                return False
        return True
    except (TypeError, ValueError):
        return False
