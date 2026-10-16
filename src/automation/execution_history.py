from datetime import datetime, timezone


class ExecutionHistory:
    def __init__(self):
        self.records = []

    def add(self, task, status, result=None, error=None):
        record = {
            "task": task,
            "status": status,
            "result": result,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.records.append(record)
        return record

    def list(self, limit=None):
        items = self.records
        return items if limit is None else items[-max(0, limit):]

    def clear(self):
        self.records.clear()
