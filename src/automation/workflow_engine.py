class WorkflowEngine:
    def __init__(self, runner=None, approval_manager=None):
        self.runner = runner
        self.approval_manager = approval_manager

    def execute(
        self,
        task_name,
        function,
        *args,
        requires_approval=False,
        approval_request=None,
        **kwargs,
    ):
        if self.runner is None:
            raise RuntimeError("A TaskRunner is required")

        if requires_approval:
            if self.approval_manager is None:
                raise PermissionError("Approval manager is not configured")

            if approval_request is None:
                request = self.approval_manager.request(task_name)
                return {
                    "status": "awaiting_approval",
                    "task": task_name,
                    "approval_request": request,
                }

            if approval_request.task != task_name:
                raise PermissionError("Approval request does not match task")

            if not self.approval_manager.is_approved(approval_request):
                return {
                    "status": "awaiting_approval",
                    "task": task_name,
                    "approval_request": approval_request,
                }

        result = self.runner.run(task_name, function, *args, **kwargs)
        return {"status": "completed", "task": task_name, "result": result}
