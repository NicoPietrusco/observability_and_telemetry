from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.endpoints import end2 as end2_module


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip the intentional delays, so the tests stay fast."""

    async def instant(_seconds):
        return None

    # Replace the module's `asyncio` only, not the real asyncio.sleep the test client runs on.
    monkeypatch.setattr(end2_module, "asyncio", SimpleNamespace(sleep=instant))


@pytest.mark.anyio
async def test_normalize():
    assert await end2_module.normalize("  HeLLo ") == "hello"


@pytest.mark.anyio
async def test_reverse():
    assert await end2_module.reverse("abc") == "cba"


@pytest.mark.anyio
async def test_validate_rejects_empty_text():
    with pytest.raises(HTTPException) as excinfo:
        await end2_module.validate("")
    assert excinfo.value.status_code == 400


def test_end2_normalizes_and_reverses(client):
    response = client.get("/end2/", params={"text": "HelloWorld"})

    assert response.status_code == 200
    body = response.json()
    assert body["input"] == "HelloWorld"
    assert body["normalized"] == "helloworld"
    assert body["reversed"] == "dlrowolleh"


def test_end2_records_one_span_per_step(client, spans):
    client.get("/end2/", params={"text": "abc"})

    names = [span.name for span in spans.get_finished_spans()]
    assert [n for n in names if n in {"normalize", "validate", "reverse", "end2"}] == [
        "normalize",
        "validate",
        "reverse",
        "end2",
    ]


def test_end2_whitespace_only_text_is_a_client_error(client):
    # Whitespace passes the query's min_length, then normalizes to an empty string.
    response = client.get("/end2/", params={"text": "   "})

    assert response.status_code == 400
    assert response.json() == {"detail": "text must not be empty"}


def test_end2_empty_text_fails_query_validation(client):
    assert client.get("/end2/", params={"text": ""}).status_code == 422
