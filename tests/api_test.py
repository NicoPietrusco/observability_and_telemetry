import pytest

from app.api import app


@pytest.fixture
def failing_route():
    """A route that raises, to reach the middleware's server error branch."""

    async def boom():
        raise RuntimeError("boom")

    app.add_api_route("/test-boom", boom)
    yield "/test-boom"
    app.router.routes = [
        r for r in app.router.routes if getattr(r, "path", None) != "/test-boom"
    ]


def request_logs(records, path):
    return [r for r in records if r["extra"].get("endpoint") == path]


def test_successful_request_is_logged_as_info(client, log_records):
    client.get("/end1/9")

    (record,) = request_logs(log_records, "/end1/9")
    assert record["level"].name == "INFO"
    assert record["message"] == "request completed"
    extra = record["extra"]
    assert extra["method"] == "GET"
    assert extra["status_code"] == 200
    assert extra["latency_ms"] >= 0
    assert "error_type" not in extra


def test_client_error_is_logged_as_warning(client, log_records):
    client.get("/end1/-1")

    (record,) = request_logs(log_records, "/end1/-1")
    assert record["level"].name == "WARNING"
    assert record["message"] == "client error"
    assert record["extra"]["error_type"] == "HTTP_400"


def test_request_log_carries_the_trace_id(client, log_records):
    body = client.get("/end1/1").json()

    (record,) = request_logs(log_records, "/end1/1")
    assert body["trace_id"] is not None
    assert record["extra"]["trace_id"] == body["trace_id"]


def test_unhandled_exception_returns_500_and_logs_error(
    client, log_records, failing_route
):
    response = client.get(failing_route)

    assert response.status_code == 500
    assert response.json() == {"error": "RuntimeError"}
    (record,) = request_logs(log_records, failing_route)
    assert record["level"].name == "ERROR"
    assert record["extra"]["error_type"] == "RuntimeError"


def test_metrics_endpoint_exposes_request_counters(client):
    client.get("/end1/4")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
