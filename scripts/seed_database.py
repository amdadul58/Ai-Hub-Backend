import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.base import initialize_database


def main():
    result = initialize_database()
    print(f"Database initialization: {result}")


if __name__ == "__main__":
    main()
