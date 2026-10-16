from dataclasses import dataclass


@dataclass
class Conversation:
    id: int | None = None
    user_id: int | None = None
    title: str = "New conversation"
