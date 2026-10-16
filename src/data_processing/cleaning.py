def clean_dataframe(df, *, drop_duplicates=True, drop_empty_rows=False, strip_strings=True):
    """Return a cleaned copy of a pandas-compatible DataFrame."""
    result = df.copy()
    if strip_strings:
        for column in result.select_dtypes(include=["object", "string"]).columns:
            result[column] = result[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
    if drop_duplicates:
        result = result.drop_duplicates()
    if drop_empty_rows:
        result = result.dropna(how="all")
    return result
