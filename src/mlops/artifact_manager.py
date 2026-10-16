import json
from pathlib import Path


class ArtifactManager:
    def __init__(self, base_dir="artifacts/mlops"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, name, data):
        if Path(name).name != name or not name.endswith(".json"):
            raise ValueError("Use a simple .json filename.")
        path = self.base_dir / name
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        temporary.replace(path)
        return str(path)

    def read_json(self, name):
        if Path(name).name != name or not name.endswith(".json"):
            raise ValueError("Use a simple .json filename.")
        path = self.base_dir / name
        return json.loads(path.read_text(encoding="utf-8"))

    def list_artifacts(self):
        return sorted(p.name for p in self.base_dir.iterdir() if p.is_file())
