from src.database.repositories.traffic_repository import TrafficRepository


class TrafficService:
    def __init__(self, repository=None):
        self.repository = repository or TrafficRepository()

    def record_event(self, event_type, location=None, details=None):
        if not event_type or not event_type.strip():
            raise ValueError("event_type cannot be empty.")
        return self.repository.create(event_type.strip(), location, details)

    def recent_events(self, limit=100):
        return self.repository.list_recent(limit)
