import os
import tempfile

import pytest

# app.api sets up tracing and logging on import, so point them somewhere harmless first:
# logs go to a temporary directory, and no collector listens on the OTLP endpoint.
os.environ.setdefault("LOG_DIR", tempfile.mkdtemp(prefix="telemetry-demo-logs-"))
os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:1")
os.environ.setdefault("OTEL_EXPORTER_OTLP_TIMEOUT", "1")

from fastapi.testclient import TestClient  # noqa: E402
from loguru import logger  # noqa: E402
from opentelemetry import trace  # noqa: E402
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: E402
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (  # noqa: E402
    InMemorySpanExporter,
)

from app.api import app  # noqa: E402

_span_exporter = InMemorySpanExporter()
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(_span_exporter))


@pytest.fixture
def anyio_backend():
    """Run the `@pytest.mark.anyio` tests on asyncio, as uvicorn does."""
    return "asyncio"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def spans():
    """Finished spans recorded during the test, oldest first."""
    _span_exporter.clear()
    yield _span_exporter
    _span_exporter.clear()


@pytest.fixture
def log_records():
    """Loguru records emitted during the test."""
    records = []
    sink_id = logger.add(lambda message: records.append(message.record), level="DEBUG")
    yield records
    logger.remove(sink_id)
