import logging
import time
import uuid
from fastapi import Request, Response, FastAPI

LOG = logging.getLogger("app.request")

def install_request_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        start = time.time()
        try:
            response: Response = await call_next(request)
        except Exception:
            LOG.exception("Unhandled error", extra={"rid": rid, "path": request.url.path})
            raise
        dur_ms = int((time.time() - start) * 1000)
        LOG.info(
            "%s %s -> %s (%sms)",
            request.method, request.url.path, response.status_code, dur_ms,
            extra={"rid": rid},
        )
        response.headers["X-Request-Id"] = rid
        return response
