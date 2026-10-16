def build_mlp(input_features, output_features, hidden_features=(64, 32), dropout=0.1):
    """Build a small fully connected PyTorch network."""
    import torch.nn as nn
    if input_features < 1 or output_features < 1:
        raise ValueError("Input and output feature counts must be positive.")
    if not 0 <= dropout < 1:
        raise ValueError("dropout must be in [0, 1).")
    layers = []
    previous = input_features
    for width in hidden_features:
        if width < 1:
            raise ValueError("Hidden layer widths must be positive.")
        layers.extend([nn.Linear(previous, width), nn.ReLU()])
        if dropout:
            layers.append(nn.Dropout(dropout))
        previous = width
    layers.append(nn.Linear(previous, output_features))
    return nn.Sequential(*layers)
