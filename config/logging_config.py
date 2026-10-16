"""Logging configuration for AI Hub."""

import logging
import os
from pathlib import Path


def configure_logging():
    """Configure application logging without duplicating handlers."""
    project_root = Path(__file__).resolve().parents[1]
    log_dir = Path(
        os.getenv("LOG_DIR", str(project_root / "logs"))
    ).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)

    level_name = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        raise ValueError(f"Invalid LOG_LEVEL: {level_name}")

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("ai_hub")
