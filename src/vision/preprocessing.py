def resize_image(image, size=(224, 224)):
    if len(size) != 2 or min(size) < 1:
        raise ValueError("size must be a positive (width, height) pair.")
    return image.resize(tuple(size))


def image_to_tensor(image):
    """Convert a PIL image to a normalized CHW float tensor."""
    import numpy as np
    import torch
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(array).permute(2, 0, 1).contiguous()
