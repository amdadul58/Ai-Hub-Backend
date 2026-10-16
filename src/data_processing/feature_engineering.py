def add_numeric_interaction(df, first, second, output_name=None):
    """Add a product feature for two existing numeric columns."""
    if first not in df.columns or second not in df.columns:
        raise ValueError("Both input columns must exist.")
    name = output_name or f"{first}_x_{second}"
    result = df.copy()
    result[name] = result[first] * result[second]
    return result


def add_datetime_features(df, column, prefix=None):
    """Add year, month, day and weekday columns from a datetime-like column."""
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")
    result = df.copy()
    dates = __import__("pandas").to_datetime(result[column], errors="coerce")
    base = prefix or column
    result[f"{base}_year"] = dates.dt.year
    result[f"{base}_month"] = dates.dt.month
    result[f"{base}_day"] = dates.dt.day
    result[f"{base}_weekday"] = dates.dt.dayofweek
    return result
