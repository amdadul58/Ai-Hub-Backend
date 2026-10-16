from sklearn.preprocessing import StandardScaler, MinMaxScaler


def make_standard_scaler():
    """Create a scaler that standardizes features."""
    return StandardScaler()


def make_minmax_scaler(feature_range=(0, 1)):
    """Create a scaler that scales features to a selected range."""
    return MinMaxScaler(feature_range=feature_range)
