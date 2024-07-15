import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.exceptions import HTTPException

from app.config.exception_handler import exception_handler, http_exception_handler
from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router.generate_simple_article_router import simple_article_router
from app.router.send_email_service_router import send_email_service_router
from app.router.user_type_router import user_type_router
from app.service.news_scheduling_service import schedule_task

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(schedule_task())


# load env
load_dotenv()

# middlewares
app.add_middleware(LoggingMiddleware)

# routers
app.include_router(user_type_router)
app.include_router(simple_article_router)
app.include_router(send_email_service_router)

# exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
