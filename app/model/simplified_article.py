from typing import Dict

from pydantic import BaseModel

class SimplifiedArticle(BaseModel):
    title: str
    content: str
    phrase: Dict[str, str]
    comment: str
    category: str