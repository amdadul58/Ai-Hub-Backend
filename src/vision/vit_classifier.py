def classify_with_vit(image, model, processor, top_k=5):
    """Run an already-loaded Hugging Face image classification model."""
    import torch
    if top_k < 1:
        raise ValueError("top_k must be positive.")
    inputs = processor(images=image, return_tensors="pt")
    model.eval()
    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0]
    values, indices = torch.topk(probabilities, min(top_k, probabilities.numel()))
    results = []
    for score, index in zip(values.tolist(), indices.tolist()):
        labels = getattr(model.config, "id2label", {})
        results.append({"label": labels.get(index, str(index)), "score": score})
    return results
