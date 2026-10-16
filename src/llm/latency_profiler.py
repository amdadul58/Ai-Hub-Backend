from time import perf_counter
from contextlib import contextmanager

@contextmanager
def measure_latency():
    start = perf_counter()
    result = {"seconds": None}
    try:
        yield result
    finally:
        result["seconds"] = round(perf_counter() - start, 6)
