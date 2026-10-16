from datetime import datetime, timezone


class NotificationService:
    """Lightweight in-process notification collector; no external delivery."""
    def __init__(self, max_items=500):
        if max_items < 1:
            raise ValueError("max_items must be positive.")
        self.max_items = max_items
        self._items = []

    def publish(self, message, category="info", recipient=None):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message cannot be empty.")
        item = {
            "message": message.strip(),
            "category": category,
            "recipient": recipient,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._items.append(item)
        self._items = self._items[-self.max_items:]
        return item

    def list_recent(self, limit=50):
        if not 1 <= limit <= self.max_items:
            raise ValueError("limit is outside the allowed range.")
        return list(reversed(self._items[-limit:]))
