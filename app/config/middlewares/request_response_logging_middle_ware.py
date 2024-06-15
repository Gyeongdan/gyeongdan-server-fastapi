import json
import time
import uuid
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.loguru_config import logger

request_id: ContextVar[str] = ContextVar("request_id")

urls_do_not_log_request = {"/translator", "/"}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id.set(str(uuid.uuid4()))

        content_type = request.headers.get("content-type", "")

        # Log the request
        body = await request.body()
        request_log = {
            "method": request.method,
            "url": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "body": None,  # Initialize body as None
            "traceId": request_id.get(),
        }

        if "application/json" in content_type:
            try:
                parsed_json = json.loads(body.decode("utf-8"))
                request_log["body"] = parsed_json
            except json.JSONDecodeError:
                logger.error("JSON decoding failed")
                request_log["body"] = "Invalid JSON format"
        elif "multipart/form-data" in content_type:
            request_log["body"] = "Multipart form data"
        else:
            try:
                request_log["body"] = body.decode("utf-8") if body else ""
            except UnicodeDecodeError:
                request_log["body"] = "Binary data"

        if request.url.path not in urls_do_not_log_request:
            logger.info(
                f"Request: {json.dumps(request_log, indent=2, ensure_ascii=False)}"
            )

        # Proceed with request handling
        response: Response = await call_next(request)

        # Read and log the response body, then recreate the response
        response_body_bytes = b"".join(
            [chunk async for chunk in response.body_iterator]
        )

        response_log = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": None,
            "time_taken": time.time() - start_time,
            "traceId": request_id.get(),
        }

        try:
            response_body = response_body_bytes.decode("utf-8")
            response_log["body"] = response_body
        except UnicodeDecodeError:
            response_log["body"] = "Binary data"

        logger.info(
            f"Response: {json.dumps(response_log, indent=2, ensure_ascii=False)}"  # pylint: disable=line-too-long
        )

        # Recreate the response object
        new_response = Response(
            content=response_body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        return new_response
