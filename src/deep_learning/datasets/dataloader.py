def make_data_loaders(train_dataset, validation_dataset=None, batch_size=32, num_workers=0):
    """Create PyTorch DataLoaders; CPU-friendly defaults use zero workers."""
    from torch.utils.data import DataLoader
    if batch_size < 1 or num_workers < 0:
        raise ValueError("batch_size must be positive and num_workers non-negative.")
    result = {"train": DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)}
    if validation_dataset is not None:
        result["validation"] = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return result
