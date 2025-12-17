import asyncio
from fastapi import APIRouter, HTTPException, Query
from opentelemetry import trace
from ..observability import trace_context

router = APIRouter()
tracer = trace.get_tracer(__name__)


async def normalize(text: str) -> str:
    with tracer.start_as_current_span("normalize"):
        await asyncio.sleep(0.5)  # slow on purpose
        return text.strip().lower()


async def validate(text: str) -> str:
    with tracer.start_as_current_span("validate"):
        await asyncio.sleep(0.5)  # slow on purpose
        if not text:
            raise HTTPException(status_code=400, detail="text must not be empty")
        return text


async def reverse(text: str) -> str:
    with tracer.start_as_current_span("reverse"):
        await asyncio.sleep(0.5)  # slow on purpose
        return text[::-1]


@router.get("/end2/")
async def end2(text: str = Query(..., min_length=1)):
    """
    Telemetry test endpoint:
    - string processing
    - intentionally slow
    - deterministic client error
    """
    with tracer.start_as_current_span("end2"):
        t1 = await normalize(text)
        t2 = await validate(t1)
        t3 = await reverse(t2)

        return {
            "input": text,
            "normalized": t1,
            "reversed": t3,
            **trace_context(),
        }
