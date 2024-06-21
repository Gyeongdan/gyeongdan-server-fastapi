from fastapi import FastAPI

from app.config.middlewares.request_response_logging_middle_ware import (
    LoggingMiddleware,
)
from app.router.news_scrap_router import news_scrap_rotuer

app = FastAPI()

app.add_middleware(LoggingMiddleware)

# news_scrapping_router를 app에 추가
app.include_router(news_scrap_rotuer)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
