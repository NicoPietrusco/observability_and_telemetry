import json

from loguru import logger
from opentelemetry import trace

from app.observability import SERVICE_NAME, setup_logging, trace_context


def test_trace_context_outside_a_span():
    assert trace_context() == {"trace_id": None, "span_id": None}


def test_trace_context_inside_a_span():
    with trace.get_tracer(__name__).start_as_current_span("test") as span:
        ctx = trace_context()

    span_ctx = span.get_span_context()
    assert ctx == {
        "trace_id": format(span_ctx.trace_id, "032x"),
        "span_id": format(span_ctx.span_id, "016x"),
    }


def test_tracer_provider_names_the_service():
    provider = trace.get_tracer_provider()
    assert provider.resource.attributes["service.name"] == SERVICE_NAME


def test_setup_logging_writes_json_lines(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    monkeypatch.setenv("LOG_DIR", str(log_dir))

    setup_logging()
    try:
        logger.bind(endpoint="/test").info("hello")
        logger.complete()
    finally:
        # Restore the handlers the rest of the suite expects (see conftest.py).
        monkeypatch.undo()
        setup_logging()

    lines = (log_dir / "app.log").read_text().splitlines()
    record = json.loads(lines[-1])["record"]
    assert record["message"] == "hello"
    assert record["extra"]["endpoint"] == "/test"
