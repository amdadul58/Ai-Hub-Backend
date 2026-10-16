from collections import deque

class AgentMemory:
    def __init__(self, max_items=50):
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self.items = deque(maxlen=max_items)

    def remember(self, task, result):
        self.items.append({"task": str(task), "result": result})

    def history(self):
        return list(self.items)

    def clear(self):
        self.items.clear()
