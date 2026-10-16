from pathlib import Path
import wave


def get_wav_info(path):
    """Read basic WAV metadata using Python's standard library."""
    with wave.open(str(Path(path)), "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        return {
            "channels": audio.getnchannels(),
            "sample_width_bytes": audio.getsampwidth(),
            "sample_rate": rate,
            "frames": frames,
            "duration_seconds": frames / rate if rate else 0.0,
        }
