from dataclasses import dataclass


@dataclass
class TrafficEvent:
    id: int | None = None
    event_type: str = ""
    location: str | None = None
