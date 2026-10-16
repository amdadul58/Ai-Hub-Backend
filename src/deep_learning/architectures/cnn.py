def build_cnn(num_classes, input_channels=3):
    """Build a compact CNN for image classification."""
    import torch.nn as nn
    if num_classes < 1 or input_channels < 1:
        raise ValueError("num_classes and input_channels must be positive.")
    return nn.Sequential(
        nn.Conv2d(input_channels, 16, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(64, num_classes),
    )
