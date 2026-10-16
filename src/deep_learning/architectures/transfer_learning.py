def build_resnet18(num_classes, pretrained=False):
    """Build a ResNet-18 classifier. Pretrained weights may require a download."""
    try:
        from torchvision.models import resnet18, ResNet18_Weights
    except ImportError as exc:
        raise RuntimeError("Transfer learning requires a compatible torchvision installation.") from exc
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = resnet18(weights=weights)
    model.fc = __import__("torch").nn.Linear(model.fc.in_features, num_classes)
    return model
