from concurrent.futures import ThreadPoolExecutor, as_completed


class TaskOrchestrator:
    """Run independent Python callables; does not itself invoke AI models."""
    def __init__(self, max_workers=2):
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1.")
        self.max_workers = int(max_workers)

    def run_one(self, function, *args, **kwargs):
        if not callable(function):
            raise TypeError("function must be callable.")
        return function(*args, **kwargs)

    def run_many(self, tasks):
        """tasks is a mapping of task names to zero-argument callables."""
        if not isinstance(tasks, dict):
            raise TypeError("tasks must be a dictionary of names to callables.")
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for name, function in tasks.items():
                if not callable(function):
                    raise TypeError(f"Task {name!r} is not callable.")
                futures[executor.submit(function)] = name
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = {"status": "success", "result": future.result()}
                except Exception as exc:
                    results[name] = {"status": "error", "error": str(exc)}
        return results
