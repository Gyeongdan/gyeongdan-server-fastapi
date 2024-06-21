from fastapi import FastAPI

from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router import article_crud_router

app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.include_router(article_crud_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
