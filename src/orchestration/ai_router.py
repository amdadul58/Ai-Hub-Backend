from src.orchestration.model_selector import select_model


class AIRouter:
    """Route task requests to registered model descriptors and handlers."""
    def __init__(self):
        self._models = {}
        self._handlers = {}

    def register(self, descriptor, handler):
        name = descriptor.get("name") if isinstance(descriptor, dict) else None
        if not name:
            raise ValueError("descriptor must include a model name.")
        if not callable(handler):
            raise TypeError("handler must be callable.")
        if name in self._models:
            raise ValueError(f"Model {name!r} is already registered.")
        self._models[name] = dict(descriptor)
        self._handlers[name] = handler

    def route(self, task, payload, preferred=None):
        descriptor = select_model(task, list(self._models.values()), preferred)
        result = self._handlers[descriptor["name"]](payload)
        return {
            "task": task,
            "model": descriptor["name"],
            "result": result,
        }

    def list_models(self):
        return list(self._models.values())
