from typing import List

import aiohttp
from fastapi import HTTPException


class AsyncGoogleSearchAPIWrapper:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def aget_relevant_documents(
        self, query: str, num_results: int = 3
    ) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cse_id,
                "num": num_results,
            }
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Google Search API request failed.",
                    )
                data = await response.json()
                return [
                    {
                        "title": item["title"],
                        "link": item["link"],
                        "snippet": item["snippet"],
                    }
                    for item in data.get("items", [])
                ]


class GoogleCSERetriever:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id

    async def retrieve(self, query: str) -> List[dict]:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={self.api_key}&cx={self.cse_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(
                        response.status, "Error retrieving data from Google."
                    )
                result = await response.json()
                items = result.get("items", [])
                return [
                    {
                        "title": item["title"],
                        "snippet": item["snippet"],
                        "link": item["link"],
                    }
                    for item in items
                ]


# async def get_related_reference(query: str):
#     google_cse_api_key = os.getenv("GOOGLE_API_KEY")
#     google_cse_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
#     google_cse_retriever = GoogleCSERetriever(api_key=google_cse_engine_id,
#                                               cse_id=google_cse_api_key)
#     google_results = google_cse_retriever.retrieve(query)
#     # Step 2: 검색 결과를 벡터화하고 ChromaDB에 저장
#     chroma_db_manager = ChromaDBManager()
#     await chroma_db_manager.add_documents(google_results)
#
#     # Step 3: 저장된 문서 중에서 쿼리와 유사한 문서 검색
#     search_results = chroma_db_manager.search_documents(query)
#
#     return search_results
