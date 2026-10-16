from src.agents.planner import create_plan
from src.agents.task_router import route_task
from src.agents.memory import AgentMemory
from src.agents.audit import audit_event

class AgentWorkflow:
    def __init__(self, executor=None, memory=None):
        self.executor = executor
        self.memory = memory or AgentMemory()

    def run(self, task, **tool_kwargs):
        plan = create_plan(task)
        tool_name = route_task(task)

        if tool_name == "general_response":
            result = {
                "message": "No specialized tool matched this task.",
                "task": task,
            }
        elif self.executor is None:
            result = {"error": "No tool executor configured", "tool": tool_name}
        else:
            result = self.executor.execute(tool_name, **tool_kwargs)

        self.memory.remember(task, result)
        audit_event("workflow_completed", {"tool": tool_name})
        return {"plan": plan, "tool": tool_name, "result": result}
