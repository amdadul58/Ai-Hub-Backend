from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.automation.approval import ApprovalManager
from src.automation.task_runner import TaskRunner
from src.automation.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/automation", tags=["Automation"])

approval_manager = ApprovalManager()
runner = TaskRunner()
engine = WorkflowEngine(runner=runner, approval_manager=approval_manager)
pending_approvals = {}

def check_backend_status():
    return {"status": "available", "task": "check_backend_status"}

class AutomationRequest(BaseModel):
    requires_approval: bool = True

@router.get("/status")
def automation_status():
    return {"status": "available", "approval_required_by_default": True}

@router.post("/run-status-check")
def run_status_check(request: AutomationRequest):
    try:
        result = engine.execute(
            "check_backend_status",
            check_backend_status,
            requires_approval=request.requires_approval,
        )
        if result["status"] == "awaiting_approval":
            request_id = str(uuid4())
            pending_approvals[request_id] = result["approval_request"]
            return {
                "status": "awaiting_approval",
                "request_id": request_id,
                "task": result["task"],
                "requested_at": result["approval_request"].requested_at,
            }
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/approvals/{request_id}/approve")
def approve_task(request_id: str):
    approval = pending_approvals.get(request_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval request not found or already processed.")

    approval_manager.approve(approval)
    try:
        result = engine.execute(
            "check_backend_status",
            check_backend_status,
            requires_approval=True,
            approval_request=approval,
        )
        pending_approvals.pop(request_id, None)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
