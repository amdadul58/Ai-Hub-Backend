class AgentToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, function):
        if not name or not callable(function):
            raise ValueError("A tool name and callable function are required")
        self._tools[name] = function

    def get(self, name):
        return self._tools.get(name)

    def names(self):
        return sorted(self._tools)
