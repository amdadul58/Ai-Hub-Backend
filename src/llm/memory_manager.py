from collections import deque

class MemoryManager:
    def __init__(self, max_messages=20):
        if max_messages < 1:
            raise ValueError("max_messages must be positive")
        self.messages = deque(maxlen=max_messages)

    def add(self, role, content):
        if role not in {"system", "user", "assistant", "tool"}:
            raise ValueError("Unsupported message role")
        self.messages.append({"role": role, "content": str(content)})

    def get_history(self):
        return list(self.messages)

    def clear(self):
        self.messages.clear()
