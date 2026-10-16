def apply_column_mapping(df, mapping):
    """Rename columns using a mapping of old names to new names."""
    missing = set(mapping) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found: {sorted(missing)}")
    return df.rename(columns=mapping).copy()


def fill_missing_values(df, *, numeric_strategy="median", categorical_value="unknown"):
    """Fill numeric missing values with median or mean and text with a constant."""
    if numeric_strategy not in {"median", "mean"}:
        raise ValueError("numeric_strategy must be 'median' or 'mean'.")
    result = df.copy()
    numeric_columns = result.select_dtypes(include="number").columns
    other_columns = result.columns.difference(numeric_columns)
    for column in numeric_columns:
        fill_value = result[column].median() if numeric_strategy == "median" else result[column].mean()
        if fill_value == fill_value:
            result[column] = result[column].fillna(fill_value)
    for column in other_columns:
        result[column] = result[column].fillna(categorical_value)
    return result
