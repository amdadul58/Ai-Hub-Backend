from pathlib import Path


def analyze_image_text(image_path, prompt, image_analyzer):
    """Pass an image path and text prompt to a caller-provided analyzer."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt cannot be empty.")
    if not callable(image_analyzer):
        raise TypeError("image_analyzer must be callable.")
    result = image_analyzer(str(path), prompt.strip())
    return {"task": "image_text", "prompt": prompt.strip(), "result": result}
