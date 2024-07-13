import os
from typing import List

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env 파일에서 환경 변수 로드
load_dotenv()


class GoogleCSERetriever:
    def __init__(self, service, engine_id):
        self.service = service
        self.engine_id = engine_id

    def retrieve(self, query: str) -> List[dict]:
        try:
            results = self.service.cse().list(q=query, cx=self.engine_id).execute()
            items = results.get("items", [])
            return [
                {
                    "title": item["title"],
                    "snippet": item["snippet"],
                    "link": item["link"],
                }
                for item in items
            ]
        except HttpError as e:
            print(f"An error occurred: {e}")
            return []


# 환경 변수에서 API 키와 엔진 ID 불러오기
google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_cse_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")

# Google Custom Search API 클라이언트 초기화
google_cse_service = build("customsearch", "v1", developerKey=google_cse_api_key)

# Google CSE Retriever 초기화
google_cse_retriever = GoogleCSERetriever(
    service=google_cse_service, engine_id=google_cse_engine_id
)


def main():
    query = "남해 독일 마을"
    results = google_cse_retriever.retrieve(query)
    print(results)


if __name__ == "__main__":
    main()
