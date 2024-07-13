import os
from http.client import HTTPException
from typing import List

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.articles.rag_lang_chain.chromadb_manager import ChromaDBManager

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
google_cse_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")

# Google Custom Search API 클라이언트 초기화
google_cse_service = build("customsearch", "v1", developerKey=google_cse_api_key)

# Google CSE Retriever 초기화
google_cse_retriever = GoogleCSERetriever(
    service=google_cse_service, engine_id=google_cse_engine_id
)


def get_related_reference(query: str):
    google_results = google_cse_retriever.retrieve(query)
    if not google_results:
        raise HTTPException(status_code=404, detail="No results found from Google.")

    # Step 2: 검색 결과를 벡터화하고 ChromaDB에 저장
    chroma_db_manager = ChromaDBManager()
    chroma_db_manager.add_documents(google_results)

    # Step 3: 저장된 문서 중에서 쿼리와 유사한 문서 검색
    search_results = chroma_db_manager.search_documents(query)

    print(search_results)


if __name__ == "__main__":
    get_related_reference(query="국내총생산은 무엇인가?")
