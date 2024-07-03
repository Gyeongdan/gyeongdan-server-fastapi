from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from fastapi import HTTPException


@dataclass
class PublisherInfo:
    kr_name: Optional[str] = field(default=None)
    title_tag: Optional[str] = field(default=None)
    title_class: Optional[str] = field(default=None)
    content_div_class: Optional[str] = field(default=None)
    content_tags: Optional[List[str]] = field(default=None)
    content_attrs: Optional[Dict[str, bool]] = field(default=None)
    rss: Optional[str] = field(default=None)


class Publisher(Enum):
    HAN_KYUNG = PublisherInfo(
        kr_name="한국경제",
        title_tag="h1",
        title_class="headline",
        content_div_class="article-body",
        content_tags=["p", "br"],
        content_attrs={},
        rss="https://www.hankyung.com/feed/all-news",
    )
    MAE_KYUNG = PublisherInfo(
        kr_name="매일경제",
        title_tag="h2",
        title_class="news_ttl",
        content_div_class="news_cnt_detail_wrap",
        content_tags=["p", "br"],  # p와 br 태그 추출
        content_attrs={},
        rss="https://www.mk.co.kr/rss/40300001/",
    )
    SEOUL_KYUNG = PublisherInfo(
        kr_name="서울경제",
        title_tag="meta",
        title_class="og:title",
        content_div_class="article",
        content_tags=["p", "br"],
        content_attrs={},
    )

    @property
    def info(self) -> PublisherInfo:
        return self.value

    @classmethod
    def list_publishers(cls) -> List["Publisher"]:
        return list(cls)


def find_publisher(name: str) -> Publisher:
    for pub in Publisher:
        if pub.name == name:
            return pub
    raise HTTPException(status_code=404, detail="출판사를 찾을 수 없습니다.")
