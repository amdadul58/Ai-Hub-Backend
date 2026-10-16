from pathlib import Path


def analyze_image_with_audio(image_path, audio_path, analyzer):
    """Pass an image and audio file to a caller-provided multimodal analyzer."""
    image = Path(image_path)
    audio = Path(audio_path)
    if not image.is_file():
        raise FileNotFoundError(f"Image file not found: {image}")
    if not audio.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio}")
    if not callable(analyzer):
        raise TypeError("analyzer must be callable.")
    result = analyzer(str(image), str(audio))
    return {"task": "image_audio", "result": result}
