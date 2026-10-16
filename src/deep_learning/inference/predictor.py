def predict_batch(model, inputs, device="cpu"):
    """Run inference for a batch and return CPU tensors."""
    import torch
    model.to(device)
    model.eval()
    with torch.inference_mode():
        outputs = model(inputs.to(device))
    return outputs.detach().cpu()


def load_checkpoint(model, path, device="cpu"):
    """Load a trusted state-dictionary checkpoint into a model."""
    import torch
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    state = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model
