from sklearn.preprocessing import LabelEncoder, OneHotEncoder


def encode_labels(values):
    """Encode target labels into integers and return encoder with results."""
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(values)
    return {"encoder": encoder, "values": encoded}


def make_one_hot_encoder():
    """Create a one-hot encoder compatible with the installed sklearn."""
    return OneHotEncoder(handle_unknown="ignore")
