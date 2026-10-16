from pathlib import Path


def transcribe_audio_text(audio_path, transcriber):
    """Transcribe audio through a supplied callable; no model is loaded here."""
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if not callable(transcriber):
        raise TypeError("transcriber must be callable.")
    result = transcriber(str(path))
    return {"task": "audio_text", "transcription": result}


def synthesize_text_audio(text, synthesizer, output_path=None):
    """Send text to a supplied text-to-speech callable."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text cannot be empty.")
    if not callable(synthesizer):
        raise TypeError("synthesizer must be callable.")
    result = synthesizer(text.strip(), output_path)
    return {"task": "text_audio", "text": text.strip(), "result": result}
