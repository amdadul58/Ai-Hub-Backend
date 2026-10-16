from src.speech.audio_loader import inspect_audio
from src.speech.speech_to_text import transcribe_file


def run_transcription(audio_path, transcriber, language=None):
    metadata = inspect_audio(audio_path)
    transcript = transcribe_file(audio_path, transcriber, language)
    return {"audio": metadata, "transcription": transcript}
