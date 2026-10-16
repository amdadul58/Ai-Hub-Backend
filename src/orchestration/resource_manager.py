from threading import BoundedSemaphore


class ResourceManager:
    """Simple in-process concurrency limiter; not a hardware memory monitor."""
    def __init__(self, max_concurrent_tasks=1):
        if max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be at least 1.")
        self.max_concurrent_tasks = int(max_concurrent_tasks)
        self._semaphore = BoundedSemaphore(self.max_concurrent_tasks)

    def acquire(self, blocking=True, timeout=None):
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative.")
        if timeout is None:
            return self._semaphore.acquire(blocking=blocking)
        return self._semaphore.acquire(blocking=blocking, timeout=timeout)

    def release(self):
        self._semaphore.release()

    def run(self, function, *args, **kwargs):
        if not callable(function):
            raise TypeError("function must be callable.")
        with self._semaphore:
            return function(*args, **kwargs)
