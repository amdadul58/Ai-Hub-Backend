from dataclasses import dataclass


@dataclass
class TrainingJob:
    id: int | None = None
    job_name: str = ""
    status: str = "pending"
