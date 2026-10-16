class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, function):
        if not name or not callable(function):
            raise ValueError("Provide a tool name and callable function")
        self._tools[name] = function

    def list_tools(self):
        return sorted(self._tools.keys())

    def call(self, name, **kwargs):
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)
