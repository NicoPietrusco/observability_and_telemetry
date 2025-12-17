# src/observability.py
import sys
from loguru import logger

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

SERVICE_NAME = "telemetry-demo"


def setup_tracing() -> None:
    resource = Resource.create({"service.name": SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def setup_logging() -> None:
    logger.remove()

    # JSON logs to file
    logger.add("logs/app.log", serialize=True, level="INFO")

    # JSON logs to stdout (handy in Docker)
    logger.add(sys.stdout, serialize=True, level="INFO")


def trace_context() -> dict:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if not ctx.is_valid:
        return {"trace_id": None, "span_id": None}
    return {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
    }
