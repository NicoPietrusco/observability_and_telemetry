import asyncio
from fastapi import APIRouter, HTTPException, Query
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from ..observability import trace_context

router = APIRouter()
tracer = trace.get_tracer(__name__)


async def normalize(text: str) -> str:
    with tracer.start_as_current_span("normalize") as span:
        span.set_attribute("input.length", len(text))
        await asyncio.sleep(0.5)  # slow on purpose
        result = text.strip().lower()
        span.set_attribute("output.length", len(result))
        span.set_status(Status(StatusCode.OK))
        return result


async def validate(text: str) -> str:
    with tracer.start_as_current_span("validate") as span:
        span.set_attribute("input.text", text)
        await asyncio.sleep(0.5)  # slow on purpose
        if not text:
            span.set_status(Status(StatusCode.ERROR, "text must not be empty"))
            span.record_exception(ValueError("text must not be empty"))
            raise HTTPException(status_code=400, detail="text must not be empty")
        span.set_status(Status(StatusCode.OK))
        return text


async def reverse(text: str) -> str:
    with tracer.start_as_current_span("reverse") as span:
        span.set_attribute("input.length", len(text))
        await asyncio.sleep(0.5)  # slow on purpose
        result = text[::-1]
        span.set_status(Status(StatusCode.OK))
        return result


@router.get("/end2/")
async def end2(text: str = Query(..., min_length=1)):
    """
    Telemetry test endpoint:
    - string processing
    - intentionally slow
    - deterministic client error
    """
    with tracer.start_as_current_span("end2") as span:
        span.set_attribute("input.text", text)
        try:
            t1 = await normalize(text)
            t2 = await validate(t1)
            t3 = await reverse(t2)
            span.set_status(Status(StatusCode.OK))
            return {
                "input": text,
                "normalized": t1,
                "reversed": t3,
                **trace_context(),
            }
        except HTTPException:
            # Error already recorded in child span
            raise
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
