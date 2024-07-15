from pydantic import BaseModel


class ArticleResponse(BaseModel):
    title: str
    content: str
    pub_date: str
    image_url: str
