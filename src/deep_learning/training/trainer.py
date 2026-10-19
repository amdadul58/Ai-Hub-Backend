def train_one_epoch(model, data_loader, optimizer, loss_function, device="cpu"):
    """Train one epoch with batch and loss validation."""
    import torch

    if not isinstance(model, torch.nn.Module):
        raise TypeError("model must be a torch.nn.Module.")

    model.to(device)
    model.train()
    total_loss = 0.0
    total_items = 0

    for batch in data_loader:
        if not isinstance(batch, (tuple, list)) or len(batch) != 2:
            raise ValueError("Each training batch must contain (inputs, targets).")

        inputs, targets = batch
        if not isinstance(inputs, torch.Tensor) or not isinstance(targets, torch.Tensor):
            raise TypeError("Inputs and targets must be PyTorch tensors.")
        if inputs.ndim == 0 or targets.ndim == 0:
            raise ValueError("Inputs and targets must have a batch dimension.")
        if inputs.shape[0] == 0 or inputs.shape[0] != targets.shape[0]:
            raise ValueError("Inputs and targets must have the same non-zero batch size.")

        inputs = inputs.to(device)
        targets = targets.to(device)
        optimizer.zero_grad(set_to_none=True)

        outputs = model(inputs)
        loss = loss_function(outputs, targets)

        if not isinstance(loss, torch.Tensor) or loss.numel() != 1:
            raise ValueError("loss_function must return a scalar tensor.")
        if not torch.isfinite(loss).all().item():
            optimizer.zero_grad(set_to_none=True)
            raise ValueError("Non-finite loss detected; training stopped.")

        loss.backward()
        optimizer.step()

        batch_size = int(targets.shape[0])
        total_loss += float(loss.detach().item()) * batch_size
        total_items += batch_size

    if total_items == 0:
        raise ValueError("Training data loader produced no batches.")

    return {"loss": total_loss / total_items, "samples": total_items}


def save_checkpoint(model, path, optimizer=None, epoch=None):
    """Save model state and optional optimizer state."""
    from pathlib import Path
    import torch

    if not isinstance(model, torch.nn.Module):
        raise TypeError("model must be a torch.nn.Module.")
    if not str(path).strip():
        raise ValueError("Checkpoint path must not be empty.")
    if epoch is not None and int(epoch) < 0:
        raise ValueError("epoch must be non-negative.")

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {"model_state_dict": model.state_dict()}
    if optimizer is not None:
        payload["optimizer_state_dict"] = optimizer.state_dict()
    if epoch is not None:
        payload["epoch"] = int(epoch)

    torch.save(payload, destination)
    return str(destination.resolve())
