from dataclasses import dataclass


@dataclass
class ModelVersion:
    id: int | None = None
    model_name: str = ""
    version: str = ""
    artifact_path: str = ""
    stage: str = "staging"
