import asyncio
import os
from typing import List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()


class GoogleCSERetriever:
    def __init__(self, api_key: str, engine_id: str):
        self.api_key = api_key
        self.engine_id = engine_id

    async def retrieve(self, query: str) -> List[dict]:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                results = response.json().get("items", [])
                return [
                    {
                        "title": item["title"],
                        "snippet": item["snippet"],
                        "link": item["link"],
                    }
                    for item in results
                ]
            except httpx.HTTPStatusError as e:
                print(f"An error occurred: {e}")
                return []


# 환경 변수에서 API 키와 엔진 ID 불러오기
google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_cse_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")

# Google CSE Retriever 초기화
google_cse_retriever = GoogleCSERetriever(
    api_key=google_cse_api_key, engine_id=google_cse_engine_id
)

# FastAPI 애플리케이션 설정
app = FastAPI()


async def search(query: str):
    results = await google_cse_retriever.retrieve(query)
    print(results)
    return {"results": results}


if __name__ == "__main__":
    asyncio.run(search("마라탕"))
