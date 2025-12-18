from fastapi import APIRouter, HTTPException
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from ..observability import trace_context

router = APIRouter()
tracer = trace.get_tracer(__name__)


def square(x: float) -> float:
    with tracer.start_as_current_span("square") as span:
        result = x * x
        span.set_status(Status(StatusCode.OK))
        return result


def root(x: float) -> float:
    with tracer.start_as_current_span("root") as span:
        if x < 0:
            span.set_status(Status(StatusCode.ERROR, "value must be strictly positive"))
            span.record_exception(ValueError("value must be strictly positive"))
            raise HTTPException(
                status_code=400, detail="value must be strictly positive"
            )
        result = x**0.5
        span.set_status(Status(StatusCode.OK))
        return result


@router.get("/end1/{value}")
async def end1(value: float):
    """
    - value must be a float
    - value must be strictly positive
    """
    with tracer.start_as_current_span("end1") as span:
        span.set_attribute("input.value", value)
        try:
            squared = square(value)
            rooted = root(value)
            span.set_status(Status(StatusCode.OK))
            return {
                "value": value,
                "square": squared,
                "root": rooted,
                **trace_context(),
            }
        except HTTPException:
            # Error already recorded in child span
            raise
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
