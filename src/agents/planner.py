def create_plan(task):
    task = str(task).strip()
    if not task:
        raise ValueError("Task cannot be empty")
    return {
        "goal": task,
        "steps": [
            {"step": 1, "action": "understand_task"},
            {"step": 2, "action": "select_tool"},
            {"step": 3, "action": "execute_and_review"},
        ],
    }
