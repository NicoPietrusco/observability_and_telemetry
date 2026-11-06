import pytest
from fastapi import HTTPException

from app.endpoints.end1 import root, square


def test_square():
    assert square(3) == 9


def test_root():
    assert root(16) == 4


def test_root_rejects_negative_values():
    with pytest.raises(HTTPException) as excinfo:
        root(-1)
    assert excinfo.value.status_code == 400


def test_end1_returns_square_and_root(client):
    response = client.get("/end1/25")

    assert response.status_code == 200
    body = response.json()
    assert body["value"] == 25
    assert body["square"] == 625
    assert body["root"] == 5


def test_end1_records_nested_spans(client, spans):
    client.get("/end1/4")

    by_name = {span.name: span for span in spans.get_finished_spans()}
    assert {"end1", "square", "root"} <= by_name.keys()
    assert by_name["end1"].attributes["input.value"] == 4
    assert by_name["square"].parent.span_id == by_name["end1"].context.span_id
    assert by_name["root"].parent.span_id == by_name["end1"].context.span_id


def test_end1_negative_value_is_a_client_error(client, spans):
    response = client.get("/end1/-5")

    assert response.status_code == 400
    assert response.json() == {"detail": "value must be strictly positive"}
    root_span = next(s for s in spans.get_finished_spans() if s.name == "root")
    assert not root_span.status.is_ok
    assert root_span.events[0].name == "exception"


def test_end1_rejects_non_numeric_values(client):
    assert client.get("/end1/abc").status_code == 422
