from dataclasses import dataclass


@dataclass
class InferenceLog:
    id: int | None = None
    model_name: str = ""
    status: str = "success"
    latency_ms: float | None = None
