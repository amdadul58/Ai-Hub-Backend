from datetime import datetime, timezone


class TrafficEventLogger:
    def __init__(self):
        self._events = []

    def log(self, event_type, details=None):
        if not event_type:
            raise ValueError("event_type is required.")
        event = {"event_type": event_type, "details": details or {},
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        self._events.append(event)
        return event

    def recent(self, limit=100):
        if limit < 1:
            raise ValueError("limit must be positive.")
        return list(reversed(self._events[-limit:]))
