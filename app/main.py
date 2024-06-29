from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.exceptions import HTTPException

from app.config.exception_handler import exception_handler, http_exception_handler
from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router.article_crud_router import articles_router
from app.router.generate_simple_article_router import simple_article_router
from app.router.news_scrap_router import news_scrap_rotuer
from app.router.newsletter_article_crud_router import newsletter_article_router
from app.router.send_email_service_router import send_email_service_router
from app.router.subscription_crud_router import subscription_router

app = FastAPI()

# load env
load_dotenv()


# middlewares
app.add_middleware(LoggingMiddleware)

# routers
app.include_router(news_scrap_rotuer)
app.include_router(articles_router)
app.include_router(subscription_router)
app.include_router(newsletter_article_router)
app.include_router(send_email_service_router)

app.include_router(simple_article_router)

# exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
