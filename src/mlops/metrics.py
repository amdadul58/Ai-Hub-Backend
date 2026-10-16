from collections import defaultdict
from threading import Lock
from time import time


class MetricsCollector:
    def __init__(self):
        self._counts = defaultdict(int)
        self._durations = defaultdict(list)
        self._lock = Lock()

    def increment(self, name, amount=1):
        if amount < 0:
            raise ValueError("amount must be non-negative.")
        with self._lock:
            self._counts[name] += amount

    def observe_duration(self, name, seconds):
        if seconds < 0:
            raise ValueError("duration must be non-negative.")
        with self._lock:
            self._durations[name].append(float(seconds))

    def snapshot(self):
        with self._lock:
            return {
                "counts": dict(self._counts),
                "durations": {
                    name: {
                        "count": len(values),
                        "average_seconds": sum(values) / len(values),
                        "max_seconds": max(values),
                    }
                    for name, values in self._durations.items() if values
                },
                "timestamp": time(),
            }


metrics_collector = MetricsCollector()
