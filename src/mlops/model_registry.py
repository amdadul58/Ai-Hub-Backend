import json
import re
from datetime import datetime, timezone
from pathlib import Path


class ModelRegistry:
    def __init__(self, registry_path="artifacts/mlops/model_registry.json"):
        self.path = Path(registry_path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"models": []})

    def _read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data):
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        temp.replace(self.path)

    def register(self, name, version, artifact_path, metrics=None, stage="staging"):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise ValueError("Invalid model name.")
        if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", version):
            raise ValueError("Version must look like v1.0.0.")
        if stage not in {"staging", "production", "archived"}:
            raise ValueError("Invalid stage.")
        artifact = Path(artifact_path).resolve()
        if not artifact.is_file():
            raise FileNotFoundError(f"Model artifact not found: {artifact}")
        data = self._read()
        if any(m["name"] == name and m["version"] == version for m in data["models"]):
            raise ValueError("This model version is already registered.")
        record = {
            "name": name, "version": version, "artifact_path": str(artifact),
            "metrics": metrics or {}, "stage": stage,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        data["models"].append(record)
        self._write(data)
        return record

    def list_models(self, name=None):
        models = self._read()["models"]
        return [m for m in models if name is None or m["name"] == name]

    def set_stage(self, name, version, stage):
        if stage not in {"staging", "production", "archived"}:
            raise ValueError("Invalid stage.")
        data = self._read()
        for model in data["models"]:
            if model["name"] == name and model["version"] == version:
                model["stage"] = stage
                self._write(data)
                return model
        raise KeyError("Model version not found.")
