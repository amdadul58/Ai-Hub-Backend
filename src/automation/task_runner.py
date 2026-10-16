class TaskRunner:
    def __init__(self, history=None):
        self.history = history

    def run(self, task_name, function, *args, **kwargs):
        if not callable(function):
            raise TypeError("function must be callable")

        try:
            result = function(*args, **kwargs)
        except Exception as exc:
            if self.history:
                self.history.add(task_name, "failed", error=str(exc))
            raise

        if self.history:
            self.history.add(task_name, "completed", result=result)

        return result
