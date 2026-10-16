"""Local model path configuration for AI Hub.

Paths are configurable and no model is downloaded automatically.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_model_path(env_name, default_relative_path):
    """Resolve a model path from an environment variable or project default."""
    configured = os.getenv(env_name)
    path = Path(configured).expanduser() if configured else Path(default_relative_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path.resolve()


def get_model_paths():
    """Return common model paths without requiring the files to exist."""
    return {
        "llm": get_model_path("AI_HUB_LLM_MODEL_PATH", "models/llm"),
        "vision": get_model_path("AI_HUB_VISION_MODEL_PATH", "ai_models"),
        "speech": get_model_path("AI_HUB_SPEECH_MODEL_PATH", "models/speech"),
        "embedding": get_model_path("AI_HUB_EMBEDDING_MODEL_PATH", "models/embeddings"),
    }
