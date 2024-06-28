from pydantic import BaseModel


class ArticleResponse(BaseModel):
    title: str
    content: str
