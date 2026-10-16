from src.agents.permissions import check_permission
from src.agents.audit import audit_event

class ToolExecutor:
    def __init__(self, registry, allowed_tools=None):
        self.registry = registry
        self.allowed_tools = allowed_tools

    def execute(self, name, **kwargs):
        if not check_permission(name, self.allowed_tools):
            audit_event("tool_denied", {"tool": name})
            raise PermissionError(f"Tool is not allowed: {name}")

        function = self.registry.get(name)
        if function is None:
            audit_event("tool_not_found", {"tool": name})
            raise KeyError(f"Tool not registered: {name}")

        result = function(**kwargs)
        audit_event("tool_executed", {"tool": name})
        return result
