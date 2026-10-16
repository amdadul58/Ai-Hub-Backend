def train_one_epoch(model, data_loader, optimizer, loss_function, device="cpu"):
    """Train one epoch; each batch must be (inputs, targets)."""
    import torch
    model.to(device)
    model.train()
    total_loss, total_items = 0.0, 0
    for inputs, targets in data_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad(set_to_none=True)
        outputs = model(inputs)
        loss = loss_function(outputs, targets)
        loss.backward()
        optimizer.step()
        batch_size = int(targets.shape[0])
        total_loss += float(loss.detach().item()) * batch_size
        total_items += batch_size
    if not total_items:
        raise ValueError("Training data loader produced no batches.")
    return {"loss": total_loss / total_items, "samples": total_items}


def save_checkpoint(model, path, optimizer=None, epoch=None):
    """Save a model state dictionary and optional optimizer state."""
    from pathlib import Path
    import torch
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model_state_dict": model.state_dict()}
    if optimizer is not None:
        payload["optimizer_state_dict"] = optimizer.state_dict()
    if epoch is not None:
        payload["epoch"] = int(epoch)
    torch.save(payload, destination)
    return str(destination.resolve())
