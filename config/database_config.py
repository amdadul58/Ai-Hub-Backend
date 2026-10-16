"""Database configuration helpers compatible with AI Hub's SQLite setup."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_database_path():
    """Return the configured SQLite database path.

    AI_HUB_DATABASE_PATH is also used by isolated automated tests.
    """
    configured = os.getenv("AI_HUB_DATABASE_PATH")
    if configured:
        return Path(configured).expanduser().resolve()

    return (PROJECT_ROOT / "artifacts" / "ai_hub.sqlite3").resolve()


def get_database_url():
    """Return a SQLAlchemy-style SQLite URL for tooling that needs one."""
    path = get_database_path()
    return "sqlite:///" + path.as_posix()
