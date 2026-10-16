def make_optimizer(model_parameters, name="adam", learning_rate=0.001, weight_decay=0.0):
    """Create a standard PyTorch optimizer."""
    import torch.optim as optim
    if learning_rate <= 0 or weight_decay < 0:
        raise ValueError("learning_rate must be positive and weight_decay non-negative.")
    choices = {"adam": optim.Adam, "adamw": optim.AdamW, "sgd": optim.SGD}
    key = name.strip().lower()
    if key not in choices:
        raise ValueError(f"Unsupported optimizer: {name}")
    return choices[key](model_parameters, lr=learning_rate, weight_decay=weight_decay)
