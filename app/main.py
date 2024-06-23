from fastapi import FastAPI
from starlette.exceptions import HTTPException

from app.config.exception_handler import exception_handler, http_exception_handler
from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router.article_crud_router import articles_router
from app.router.news_scrap_router import news_scrap_rotuer

app = FastAPI()

# middlewares
app.add_middleware(LoggingMiddleware)

# routers
app.include_router(news_scrap_rotuer)
app.include_router(articles_router)
# 아 모르겠다.

# exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
