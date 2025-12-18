import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from .observability import setup_logging, setup_tracing, trace_context, SERVICE_NAME
from .endpoints import end1_router, end2_router

setup_tracing()
setup_logging()

app = FastAPI()

# Tracing
FastAPIInstrumentor.instrument_app(app)

# Metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(end1_router)
app.include_router(end2_router)


@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        # Classify log level + error_type based on final status code
        status = response.status_code
        level = "info"
        error_type = None
        message = "request completed"

        if 400 <= status < 500:
            level = "warning"
            message = "client error"
            error_type = f"HTTP_{status}"  # e.g. HTTP_400, HTTP_422

        extra = dict(
            service=SERVICE_NAME,
            endpoint=request.url.path,
            method=request.method,
            status_code=status,
            latency_ms=latency_ms,
            **trace_context(),
        )
        if error_type:
            extra["error_type"] = error_type

        logger.bind(**extra).log(level.upper(), message)
        return response

    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)

        logger.bind(
            service=SERVICE_NAME,
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            latency_ms=latency_ms,
            error_type=type(exc).__name__,
            **trace_context(),
        ).error("server error")

        return JSONResponse(status_code=500, content={"error": type(exc).__name__})
