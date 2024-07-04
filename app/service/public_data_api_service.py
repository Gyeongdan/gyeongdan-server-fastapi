import os
from enum import Enum
from typing import List

import httpx


class PublicDataAPIInfo:
    def __init__(self, api_name: str, url: str, urlElements: List[str]) -> None:
        self.api_name = api_name
        self.url = url
        self.urlElements = urlElements


class PublicDataAPI(Enum):
    population = PublicDataAPIInfo(
        api_name="인구",
        url="https://apis.data.go.kr/1240000/IndicatorService/IndListSearchRequest",
        urlElements=["pageNo=1", "numOfRows=10", "STAT_JIPYO_NM=인구", "format=json"],
    )
    youth_policy = PublicDataAPIInfo(
        api_name="청소년 정책",
        url="https://apis.data.go.kr/1383000/yhis/YouthNewsService/getYouthNewsList",
        urlElements=["pageNo=1", "numOfRows=10", "type=xml&pstRegYmd=20231101"],
    )


class PublicDataAPIService:
    def __init__(self):
        self.api_key = os.getenv("PUBLIC_DATA_API_KEY")

    async def response(self, publicDataApi: PublicDataAPIInfo):
        url = publicDataApi.url + "?" + "serviceKey=" + self.api_key
        for urlElement in publicDataApi.urlElements:
            url += "&" + urlElement

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)
        return response.text
