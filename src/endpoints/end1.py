from fastapi import APIRouter, HTTPException
from opentelemetry import trace
from ..observability import trace_context

router = APIRouter()
tracer = trace.get_tracer(__name__)


def square(x: float) -> float:
    return x * x


def root(x: float) -> float:
    if x < 0:
        raise HTTPException(status_code=400, detail="value must be strictly positive")
    return x**0.5


@router.get("/end1/{value}")
async def end1(value: float):
    """
    - value must be a float
    - value must be strictly positive
    """
    with tracer.start_as_current_span("end1"):
        squared = square(value)
        rooted = root(value)

        return {
            "value": value,
            "square": squared,
            "root": rooted,
            **trace_context(),
        }
