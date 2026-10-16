from datetime import datetime, timezone


class ModelMonitor:
    def __init__(self):
        self._events = []

    def record(self, model_name, event_type, success=True, latency_ms=None, details=None):
        if latency_ms is not None and latency_ms < 0:
            raise ValueError("latency_ms must be non-negative.")
        event = {
            "model_name": model_name,
            "event_type": event_type,
            "success": bool(success),
            "latency_ms": latency_ms,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._events.append(event)
        return event

    def summary(self):
        count = len(self._events)
        latencies = [e["latency_ms"] for e in self._events if e["latency_ms"] is not None]
        return {
            "total_events": count,
            "failed_events": sum(not e["success"] for e in self._events),
            "average_latency_ms": sum(latencies) / len(latencies) if latencies else None,
            "events": list(self._events),
        }


model_monitor = ModelMonitor()
