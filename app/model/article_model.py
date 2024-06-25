from pydantic import BaseModel


class ArticleResponse(BaseModel):
    title: str
    content: str

# 뉴스 유형별 HTML 구조 설정
news_settings = {
    "MAE_KYUNG": {
        "title_tag": "h2",
        "title_class": "news_ttl",
        "content_div_class": "news_cnt_detail_wrap",
        "content_tags": ["p"],
        "content_attrs": {"refid": True}
    },
    "HAN_KYUNG": {
        "title_tag": "h1",
        "title_class": "headline",
        "content_div_class": "article-body",
        "content_tags": ["p", "br"],
        "content_attrs": {}
    },
    "SEOUL_KUNG": {
        "title_tag": "div",
        "title_class": "headline",
        "content_div_class": "article",
        "content_tags": ["p", "br"],
        "content_attrs": {}
    }
}