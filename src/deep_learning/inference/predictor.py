def predict_batch(model, inputs, device="cpu"):
    """Run validated inference and return CPU tensors."""
    import torch

    if not isinstance(model, torch.nn.Module):
        raise TypeError("model must be a torch.nn.Module.")
    if not isinstance(inputs, torch.Tensor):
        raise TypeError("inputs must be a PyTorch tensor.")
    if inputs.ndim == 0 or inputs.shape[0] == 0:
        raise ValueError("inputs must have a non-empty batch dimension.")

    model.to(device)
    model.eval()

    with torch.inference_mode():
        outputs = model(inputs.to(device))

    if not isinstance(outputs, torch.Tensor):
        raise TypeError("The model must return a PyTorch tensor.")
    if outputs.ndim == 0 or outputs.shape[0] != inputs.shape[0]:
        raise ValueError("Model output batch size does not match input batch size.")
    if not torch.isfinite(outputs).all().item():
        raise RuntimeError("Model produced non-finite inference outputs.")

    return outputs.detach().cpu()


def load_checkpoint(model, path, device="cpu"):
    """Load a trusted state-dictionary checkpoint safely."""
    from pathlib import Path
    import torch

    if not isinstance(model, torch.nn.Module):
        raise TypeError("model must be a torch.nn.Module.")

    checkpoint_path = Path(path)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=True,
    )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    if not isinstance(state_dict, dict) or not state_dict:
        raise ValueError("Checkpoint does not contain a valid model state dictionary.")

    model.load_state_dict(state_dict, strict=True)
    model.to(device)
    model.eval()
    return model
