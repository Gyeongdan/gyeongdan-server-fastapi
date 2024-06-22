from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from fastapi import HTTPException


@dataclass
class PublisherInfo:
    name: str
    crawled_class: Optional[str] = field(default=None)  # 크롤링 클래스


class Publisher(Enum):
    HAN_KYUNG = "한국경제"
    MAE_KYUNG = "매일경제"
    SEOUL_KUNG = "서울경제"

    def __init__(self, name: str):
        self._info = PublisherInfo(name=name, crawled_class="")

    @property
    def info(self) -> PublisherInfo:
        return self._info


def find_publisher(name: str) -> Publisher:
    for pub in Publisher:
        if pub.name == name:
            return pub
    raise HTTPException(status_code=404, detail="출판사를 찾을 수 없습니다.")
