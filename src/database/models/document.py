from dataclasses import dataclass


@dataclass
class Document:
    id: int | None = None
    filename: str = ""
    file_path: str = ""
    content_type: str | None = None
    status: str = "uploaded"
