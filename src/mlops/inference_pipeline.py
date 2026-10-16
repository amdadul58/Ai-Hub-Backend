from time import perf_counter


def run_inference(model, inputs, model_name="unnamed"):
    """Run predict() and return outputs plus measured latency."""
    start = perf_counter()
    try:
        if not hasattr(model, "predict"):
            raise TypeError("Model must expose a predict() method.")
        predictions = model.predict(inputs)
        return {
            "model_name": model_name,
            "predictions": predictions.tolist() if hasattr(predictions, "tolist") else predictions,
            "latency_ms": (perf_counter() - start) * 1000,
            "status": "success",
        }
    except Exception as exc:
        return {
            "model_name": model_name,
            "latency_ms": (perf_counter() - start) * 1000,
            "status": "error",
            "error": str(exc),
        }
