import os
from pathlib import Path
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_database_path():
    """Legacy SQLite path, retained for backup and migration utilities."""
    configured = os.getenv("AI_HUB_DATABASE_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return (PROJECT_ROOT / "artifacts" / "ai_hub.sqlite3").resolve()


def get_database_url():
    url = os.getenv("AI_HUB_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "AI_HUB_DATABASE_URL is missing. Configure it in the project .env file."
        )
    return url


def get_connection():
    """Open a PostgreSQL connection with dictionary-style result rows."""
    return psycopg.connect(get_database_url(), row_factory=dict_row)


@contextmanager
def database_connection():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
