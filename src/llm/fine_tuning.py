def check_fine_tuning_dependencies():
    missing = []
    for package in ("torch", "transformers", "datasets", "peft"):
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return {
        "available": not missing,
        "missing_packages": missing,
        "note": "Fine-tuning is optional; CPU training may be slow."
    }
