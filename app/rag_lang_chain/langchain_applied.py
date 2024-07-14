import os
from typing import List, Union

import aiohttp
from fastapi import HTTPException
from langchain.schema import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.config.loguru_config import logger
from app.rag_lang_chain.chromadb_manager import ChromaDBManager
from app.rag_lang_chain.google_cse_retriver import (
    AsyncGoogleSearchAPIWrapper,
    GoogleCSERetriever,
)


class RagAppliedResult:
    result_text: str
    related_documents: List[Union[Document, dict]]


async def request_rag_applied_openai(
    original_text: str,  # OriginalText: 기사 원문(Google Custom Search에 보낼 용도)
    system_prompt: str,  # SystemPrompt: 시스템 프롬프트
) -> RagAppliedResult:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    search = AsyncGoogleSearchAPIWrapper(api_key=google_api_key, cse_id=google_cse_id)
    google_cse_retriever = GoogleCSERetriever(
        api_key=google_api_key, cse_id=google_cse_id
    )

    # Step 1: Google Custom Search API를 사용하여 관련 정보 수집
    google_results = await google_cse_retriever.retrieve(
        original_text
    )  # FIXME: 왜 GoogleCSERetriever를 사용하는가? # pylint: disable=fixme
    if not google_results:
        raise HTTPException(status_code=404, detail="No results found from Google.")

    # Step 2: 검색 결과를 벡터화하고 ChromaDB에 저장
    chroma_db_manager = ChromaDBManager()
    await chroma_db_manager.add_documents(google_results)

    # Step 3: 저장된 문서 중에서 쿼리와 유사한 문서 검색, AsyncGoogleSearchAPIWrapper를 사용하여 추가 정보 수집
    search_results = await chroma_db_manager.search_documents(original_text)
    additional_info = await search.aget_relevant_documents(original_text, num_results=3)

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

    logger.info(f"Response: {response.generations[0][0].text}")

    # response.generations[0][0].text

    return RagAppliedResult(
        result_text=response.generations[0][0].text,
        related_documents=search_results + additional_info,
    )


# RAG 적용 프롬프트 생성(원래 프롬프트를 넣으면 유사 정보를 추가하여 반환)
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
