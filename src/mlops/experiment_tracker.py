import json
from datetime import datetime, timezone
from pathlib import Path


class ExperimentTracker:
    def __init__(self, path="artifacts/mlops/experiments.jsonl"):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, experiment_name, parameters=None, metrics=None, tags=None):
        if not experiment_name or not experiment_name.strip():
            raise ValueError("experiment_name cannot be empty.")
        record = {
            "experiment_name": experiment_name.strip(),
            "parameters": parameters or {},
            "metrics": metrics or {},
            "tags": tags or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, default=str) + "\n")
        return record

    def list_runs(self, experiment_name=None):
        if not self.path.exists():
            return []
        runs = []
        with self.path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    record = json.loads(line)
                    if experiment_name is None or record.get("experiment_name") == experiment_name:
                        runs.append(record)
        return runs
