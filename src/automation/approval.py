from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ApprovalRequest:
    task: str
    approved: bool = False
    requested_at: str = ""

    def __post_init__(self):
        if not self.requested_at:
            self.requested_at = datetime.now(timezone.utc).isoformat()


class ApprovalManager:
    def __init__(self):
        self.requests = []

    def request(self, task):
        item = ApprovalRequest(task=task)
        self.requests.append(item)
        return item

    def approve(self, request):
        request.approved = True
        return request

    def is_approved(self, request):
        return request.approved
