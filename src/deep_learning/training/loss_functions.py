def make_loss(name="cross_entropy"):
    """Create a standard PyTorch loss function."""
    import torch.nn as nn
    choices = {
        "cross_entropy": nn.CrossEntropyLoss,
        "mse": nn.MSELoss,
        "l1": nn.L1Loss,
        "bce_with_logits": nn.BCEWithLogitsLoss,
    }
    key = name.strip().lower()
    if key not in choices:
        raise ValueError(f"Unsupported loss: {name}")
    return choices[key]()
