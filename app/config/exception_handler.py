import json
import traceback

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

from app.config.loguru_config import logger


def log_exception(
    request: Request, exc: Exception  # pylint: disable=unused-argument
) -> None:
    stack_trace = traceback.format_exc()
    log_entry = {
        "error.message": str(exc),
        "error.type": exc.__class__.__name__,
        "error.stacktrace": stack_trace,
    }
    logger.error(json.dumps(log_entry))


async def http_exception_handler(request: Request, exc: HTTPException):
    log_exception(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "message": exc.detail,
            "stack_trace": traceback.format_exc(),
        },
    )


async def exception_handler(request: Request, exc: Exception):
    log_exception(request, exc)
    return JSONResponse(
        status_code=500,
        content={
            "result": False,
            "message": "Internal server error",
            "stack_trace": traceback.format_exc(),
        },
    )
