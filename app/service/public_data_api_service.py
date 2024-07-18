import os
from enum import Enum

import httpx
from pydantic import BaseModel


class PublicDataAPIInfo(BaseModel):
    api_name: str
    url: str
    urlElements: list


class PublicDataAPI(Enum):
    population = {
        "api_name": "인구",
        "url": "https://apis.data.go.kr/1240000/IndicatorService/IndListSearchRequest",
        "urlElements": [
            "pageNo=1",
            "numOfRows=10",
            "STAT_JIPYO_NM=인구",
            "format=json",
        ],
    }
    youth_policy = {
        "api_name": "청소년 정책",
        "url": "https://apis.data.go.kr/1383000/yhis/YouthNewsService/getYouthNewsList",
        "urlElements": ["pageNo=1", "numOfRows=10", "type=xml&pstRegYmd=20231101"],
    }
    jinju_covid = {
        "api_name": "진주 코비드",
        "url": "https://api.odcloud.kr/api/15099487/v1/uddi:53930f47-e995-47a2-ac7c-a81ae91c3b4c",
        "urlElements": ["page=1", "perPage=40", "type=json"],
    }


class PublicDataAPIService:
    def __init__(self):
        self.api_key = os.getenv("PUBLIC_DATA_API_KEY")

    async def response(self, publicDataApi):
        # 임시 데이터
        data = PublicDataAPI.population
        for temp in PublicDataAPI:
            # str로 체크!
            if temp.value["api_name"] == publicDataApi:
                data = temp
        url = data.value["url"] + "?" + "serviceKey=" + self.api_key
        for urlElement in data.value["urlElements"]:
            url += "&" + urlElement

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)
        return response.text
