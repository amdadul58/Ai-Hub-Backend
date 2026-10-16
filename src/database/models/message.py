from dataclasses import dataclass


@dataclass
class Message:
    id: int | None = None
    conversation_id: int = 0
    role: str = "user"
    content: str = ""
