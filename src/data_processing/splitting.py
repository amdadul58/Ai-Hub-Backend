def split_dataset(X, y, *, test_size=0.2, random_state=42, stratify=None):
    """Split features and targets using scikit-learn."""
    from sklearn.model_selection import train_test_split
    if len(X) != len(y):
        raise ValueError("X and y must contain the same number of rows.")
    if len(X) < 2:
        raise ValueError("At least two rows are required.")
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
