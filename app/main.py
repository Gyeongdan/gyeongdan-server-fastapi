import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.exceptions import HTTPException

from app.config.exception_handler import exception_handler, http_exception_handler
from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router.api_visualization_router import api_visualization_router
from app.router.chatbot_article_router import chatbot_article_router
from app.router.generate_simple_article_router import simple_article_router
from app.router.send_email_service_router import send_email_service_router
from app.router.user_type_router import user_type_router
from app.service.news_scheduling_service import schedule_task
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
origins = ["*"]  # 모든 출처 허용

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

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
app.include_router(chatbot_article_router)
app.include_router(api_visualization_router)

# exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

@app.get("/health")
async def health_check():
    return {"status": "OK"}
