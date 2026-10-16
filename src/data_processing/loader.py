from pathlib import Path
import json


def load_csv(path, **kwargs):
    """Load a CSV file as a DataFrame. Requires pandas."""
    import pandas as pd
    return pd.read_csv(Path(path), **kwargs)


def load_json(path, **kwargs):
    """Load a JSON file as Python data."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle, **kwargs)


def load_jsonl(path):
    """Load newline-delimited JSON records."""
    records = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON on line {line_number}") from exc
    return records
