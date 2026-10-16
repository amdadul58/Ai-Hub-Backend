from pathlib import Path
import wave


def inspect_audio(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    result = {"path": str(path.resolve()), "size_bytes": path.stat().st_size,
              "extension": path.suffix.lower()}
    if path.suffix.lower() == ".wav":
        with wave.open(str(path), "rb") as audio:
            result.update({
                "sample_rate": audio.getframerate(),
                "channels": audio.getnchannels(),
                "sample_width_bytes": audio.getsampwidth(),
                "frames": audio.getnframes(),
                "duration_seconds": audio.getnframes() / audio.getframerate(),
            })
    return result
