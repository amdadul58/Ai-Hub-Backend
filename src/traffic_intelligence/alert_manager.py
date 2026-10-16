class AlertManager:
    def __init__(self):
        self._alerts = []

    def raise_alert(self, level, message, details=None):
        if level not in {"info", "warning", "critical"}:
            raise ValueError("Invalid alert level.")
        alert = {"level": level, "message": str(message), "details": details or {}}
        self._alerts.append(alert)
        return alert

    def list_alerts(self):
        return list(self._alerts)
