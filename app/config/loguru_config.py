import json
import logging
import os
import socket
import sys
import traceback
from datetime import datetime

from loguru import logger

from app.config.constant import environment, service_name


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_text).log(
            level, record.getMessage()
        )


def setup_logger():
    logger.remove()

    log_file_path = f"log/{os.getenv('HOSTNAME')}-{service_name}.log"

    # Uvicorn과 애플리케이션 로그 모두 파일에 기록
    logger.add(
        log_file_path,
        rotation="5 MB",
        retention="10 days",
        compression="zip",
        format="{extra[serialized]}",
    )

    # 콘솔 출력 설정
    logger.add(
        sys.stdout,
        format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}:{function}</cyan> | {message}",  # pylint: disable=line-too-long
    )

    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").propagate = False

    logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


def serialize(record):
    try:
        message_data = json.loads(record["message"])
    except json.JSONDecodeError:
        message_data = {"message": record["message"]}

    log_entry = {
        "@timestamp": (
            record["time"].isoformat()
            if isinstance(record["time"], datetime)
            else str(record["time"])
        ),
        "@version": "1",
        "message": message_data.get("message", record["message"]),
        "service": service_name,
        "logger_name": record["name"],
        "thread_name": record["thread"].name,
        "level": record["level"].name,
        "level_value": record["level"].no,
        "HOSTNAME": socket.gethostname(),
        "environment": environment,
    }

    if "error.message" in message_data:
        error_type = message_data.get("error.type", "UnknownError")
        error_message = message_data.get("error.message", "No error message provided.")
        log_entry["message"] = f"{error_type}: {error_message}"
        log_entry["stack_trace"] = message_data["error.stacktrace"]

    if record.get("exc_info"):
        exc_type, exc_value, exc_traceback = record["exc_info"]
        stack_trace = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        log_entry["error.message"] = str(exc_value)
        log_entry["error.type"] = exc_type.__name__
        log_entry["error.stacktrace"] = stack_trace

    return json.dumps(log_entry)


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger = logger.patch(patching)
setup_logger()
