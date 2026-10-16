from pathlib import Path


def transcribe_file(audio_path, transcriber, language=None):
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    if not callable(transcriber):
        raise TypeError("transcriber must be callable.")
    result = transcriber(str(path), language=language)
    if isinstance(result, dict):
        return result
    return {"text": str(result), "language": language}
