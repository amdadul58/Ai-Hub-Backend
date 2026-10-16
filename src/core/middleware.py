import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from src.mlops.metrics import metrics_collector


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", "").strip()

        if not request_id or len(request_id) > 100 or any(
            not (ch.isalnum() or ch in "-_.") for ch in request_id
        ):
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        started = time.perf_counter()
        status_code = 500
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            elapsed_seconds = time.perf_counter() - started

            metrics_collector.increment("http_requests_total")
            metrics_collector.increment(
                f"http_requests_status_{status_code // 100}xx"
            )
            metrics_collector.increment(
                f"http_requests_method_{request.method.upper()}"
            )
            metrics_collector.observe_duration(
                "http_request", elapsed_seconds
            )

            if response is not None:
                response.headers["X-Process-Time-Ms"] = (
                    f"{elapsed_seconds * 1000:.2f}"
                )
