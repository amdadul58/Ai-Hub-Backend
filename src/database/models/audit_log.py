from dataclasses import dataclass


@dataclass
class AuditLog:
    id: int | None = None
    actor: str | None = None
    action: str = ""
    resource: str | None = None
