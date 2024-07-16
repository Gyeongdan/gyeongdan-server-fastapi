import os

import aiohttp
from fastapi import HTTPException
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.config.loguru_config import logger
from app.rag_lang_chain.chromadb_manager import ChromaDBManager
from app.rag_lang_chain.google_cse_retriver import (
    AsyncGoogleSearchAPIWrapper,
    GoogleCSERetriever,
)

from langchain.schema import Document

from typing import List, Union, Dict


class RagAppliedResult:
    def __init__(self, result_text: str, related_documents: List[Union[Document, dict]]):
        self.result_text = result_text
        self.related_documents = related_documents

    def to_dict(self) -> Dict:
        related_docs = []
        for doc in self.related_documents:
            if isinstance(doc, Document):
                related_docs.append({
                    'title': doc.metadata.get('title', 'No title'),
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'No source')
                })
            else:
                related_docs.append(doc)
        return {
            'result_text': self.result_text,
            'related_documents': related_docs
        }


async def request_rag_applied_openai(
        original_text: str,  # OriginalText: 기사 원문(Google Custom Search에 보낼 용도)
        system_prompt: str,  # SystemPrompt: 시스템 프롬프트
) -> Dict:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    search = AsyncGoogleSearchAPIWrapper(api_key=google_api_key, cse_id=google_cse_id)
    google_cse_retriever = GoogleCSERetriever(
        api_key=google_api_key, cse_id=google_cse_id
    )

    # Step 1: Google Custom Search API를 사용하여 사용자가 입력한 original_text 관련 정보 전부 수집
    # original_text와 관련된 웹 페이지의 목록을 반환함. 각 웹 페이지는 title(검색 결과 제목), link(웹 페이지 url), snippet(검색 결과의 요약)으로 구성됨.
    google_results = await google_cse_retriever.retrieve(
        original_text
    )
    if not google_results:
        raise HTTPException(status_code=404, detail="No results found from Google.")
    logger.info(f"1. Google results: {google_results}")

    # Step 2: 검색 결과를 벡터화하고 ChromaDB에 저장
    chroma_db_manager = ChromaDBManager()
    await chroma_db_manager.add_documents(google_results)

    # Step 3: 저장된 문서 중에서 사용자 쿼리와 유사한 문서 검색, AsyncGoogleSearchAPIWrapper를 사용하여 추가 정보 수집
    search_results = await chroma_db_manager.search_documents(original_text) # 벡터 유사도 검색 수행
    logger.info(f"3. Search results: {search_results}")
    additional_info = await search.aget_relevant_documents(original_text, num_results=3)
    logger.info(f"3. Additional info: {additional_info}")

    # Step 4: 프롬프트 생성(원문 + 검색 결과 + 추가 정보)

    rag_applied_prompt = await create_rag_applied_prompt(
        original_prompt=system_prompt, relevant_info=search_results + additional_info
    )

    # Step 5: OpenAI 요청 결과 반환
    try:
        search_llm = ChatOpenAI(
            temperature=0, model="gpt-4", max_tokens=1500, api_key=openai_api_key
        )
        response = await search_llm.agenerate(
            messages=[[HumanMessage(rag_applied_prompt)]]
        )
    except aiohttp.ClientResponseError as e:
        if e.status == 429:
            raise HTTPException(
                429, "Too many requests. Please try again later."
            ) from e
        raise HTTPException(500, "Internal Server Error") from e

    logger.info(f"최종 Response: {response}")

    return RagAppliedResult(
        result_text=response.generations[0][0].text,
        related_documents=search_results + additional_info,
    ).to_dict()


async def create_rag_applied_prompt(
    original_prompt: str, relevant_info: List[Union[Document, dict]]
) -> str:
    for idx, info in enumerate(relevant_info):
        if isinstance(info, Document):
            title = info.metadata.get("title", "제목 없음")
            link = info.metadata.get("source", "URL 없음")
            snippet = info.page_content
        else:
            title = info.get("title", "제목 없음")
            link = info.get("link", "URL 없음")
            snippet = info.get("snippet", "내용 없음")
        original_prompt += (
            f"\n{idx + 1}. 제목: {title}\n   URL: {link}\n   내용: {snippet}\n"
        )

    logger.info(f"RAG Applied Prompt: {original_prompt}")
    return original_prompt
