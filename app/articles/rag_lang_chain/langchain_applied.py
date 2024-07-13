import asyncio
import os
from typing import List, Union

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from googleapiclient.discovery import build
from langchain.schema import Document, HumanMessage
from langchain_community.retrievers import WebResearchRetriever
from langchain_community.vectorstores import Chroma
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel

from app.articles.rag_lang_chain.chromadb_manager import ChromaDBManager
from app.articles.rag_lang_chain.google_cse_retriver import GoogleCSERetriever

# 환경 변수 로드
load_dotenv()

app = FastAPI()


class ArticleRequest(BaseModel):
    text: str


# Google Custom Search API 클라이언트 초기화
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")
google_cse_service = build("customsearch", "v1", developerKey=google_api_key)
google_cse_retriever = GoogleCSERetriever(
    service=google_cse_service, engine_id=google_cse_id
)

# Web Research Retriever 셋팅하기
search_llm = ChatOpenAI(
    temperature=0, model="gpt-4o", max_tokens=1500, api_key=os.getenv("OPENAI_API_KEY")
)
search = GoogleSearchAPIWrapper()
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_db_oai"
)

web_research_retriever = WebResearchRetriever.from_llm(
    vectorstore=vectorstore, llm=search_llm, search=search
)


def create_prompt(
    original_text: str, relevant_info: List[Union[Document, dict]]
) -> str:
    prompt = f"""
    너는 내가 제공하는 어려운 대한민국 경제 신문 본문을 20대 초반이 읽어도 이해하기 쉽게, 한국어로 기사를 재생성하는 기자이다.
    아래 json 형식에 맞게 기사를 재생성해야 한다. 단, 기사 본문의 경우 문단을 나누어야 한다. 줄바꿈 문자는 \\n으로 표시한다.

    다음은 json 형식의 예시이다:
    {{
        "title": "MZ세대가 흥미를 끌만한 기사 제목(한국어)",
        "content": "기사 본문 (한국어). 단, 경제 기사의 독자층이 경제 지식이 부족한 20대 초반인 것을 고려하여 적당한 이모지를 사용하여 친근하고 간결하게 설명할 것. 문단은 \\n으로 구분할 것.",
        "phrase": {{"어려웠던 경제 표현들" :  "어려웠던 경제 표현들을 쉽게 바꾼 문구"}}  (예시: {{"환율" : "다른 나라 돈과 우리나라 돈을 교환하는 비율"}}),
        "comment": "기사를 보고 추론할 수 있는 것 1문장을 친구에게 설명하는 듯한 표현으로",
        "category": "Category 중 하나"
    }}

    enum Category:
        ECONOMY_AND_BUSINESS = "경제 및 기업"
        POLITICS_AND_SOCIETY = "정치 및 사회"
        TECHNOLOGY_AND_CULTURE = "기술 및 문화"
        SPORTS_AND_LEISURE = "스포츠 및 여가"
        OPINION_AND_ANALYSIS = "오피니언 및 분석"

    결과는 json 형식이어야 한다.

    원문: {original_text}

    다음은 원문을 기반으로 한 주요 정보다:
    """
    for idx, info in enumerate(relevant_info):
        if isinstance(info, Document):
            title = info.metadata.get("title", "제목 없음")
            link = info.metadata.get("source", "URL 없음")
            snippet = info.page_content
        else:
            title = info.get("title", "제목 없음")
            link = info.get("link", "URL 없음")
            snippet = info.get("snippet", "내용 없음")
        prompt += f"\n{idx + 1}. 제목: {title}\n   URL: {link}\n   내용: {snippet}\n"
    prompt += "\n이 정보를 바탕으로 쉬운 말로 재작성해 주세요."
    return prompt


async def simplify_article(article_request: ArticleRequest):
    original_text = article_request.text

    # Step 1: Google Custom Search API를 사용하여 관련 정보 수집
    google_results = google_cse_retriever.retrieve(original_text)
    if not google_results:
        raise HTTPException(status_code=404, detail="No results found from Google.")

    # Step 2: 검색 결과를 벡터화하고 ChromaDB에 저장
    chroma_db_manager = ChromaDBManager()
    chroma_db_manager.add_documents(google_results)

    # Step 3: 저장된 문서 중에서 쿼리와 유사한 문서 검색
    search_results = chroma_db_manager.search_documents(original_text)

    print(search_results)

    # Step 4: Web Research Retriever를 사용하여 추가 정보 수집
    additional_info = search.results(original_text, num_results=3)

    # Step 5: 프롬프트 생성
    prompt = create_prompt(
        original_text=original_text, relevant_info=search_results + additional_info
    )

    # Step 6: OpenAI API를 통해 기사 생성
    messages = [HumanMessage(content=prompt)]
    response = search_llm.invoke(messages)

    print(response.content)

    return {"simplified_text": response.content}


if __name__ == "__main__":
    asyncio.run(
        simplify_article(
            ArticleRequest(
                text="""
일본 정부가 올해 발간한 ‘방위백서’에서 한국을 처음으로 협력 파트너이자 중요한 이웃나라로 규정했다. 하지만 20년째 “독도는 일본 고유영토”라는 억지 주장도 이어갔다.
일본 정부는 12일 열린 각의(국무회의)에서 ‘2024년도 방위백서’를 채택했다. 올해 방위백서에서는 최근 달라진 한일 관계에 대한 기술이 추가됐다.
대표적으로 한국에 대해 “국제사회에서 여러 과제 대응에 파트너로 협력해 나가야 할 중요한 이웃나라”라고 표현했다. 일본 정부가 방위백서에서 한국을 협력 파트너로 명기한 것은 이번이 처음이다.
또 한국 관련 사진을 지난해 1장에서 올해 4장으로, 관련 내용도 지난해 2페이지에서 올해 3.5페이지로 각각 늘렸다. 일본 정부는 앞서 지난 4월 펴낸 ‘외교청서’에서 2010년 이후 14년 만에 한국을 ‘파트너’라고 표현했는데, 이러한 흐름을 방위백서에도 반영한 것으로 보인다.
지난달 싱가포르에서 개최된 한일 국방장관 회담 내용도 소개했다. 이 회담에서 양국 국방현안이었던 초계기 갈등과 관련해 재발 방지를 위해 한국 해군참모총장과 일본 해상막료장 간 합의문을 작성했다고 소개했다. 현재 언론은 방위백서는 통상 3월까지의 일을 기재하는데 6월에 있은 양국 국방장관 회담을 기술한 것은 이례적이라는 분석을 내놓고 있다.
한미일 간 협력과 관련해서는 작년 8월 미국 캠프데이비드에서 열린 한미일 3국 정상회의 사진을 싣고는 “북한의 미사일 경계 데이터의 실시간 공유의 운용 개시를 향한 진전을 확인했다”고 적었다.
반면 독도에 대한 기술은 지난해와 동일한 내용을 이어갔다. 방위성은 인도·태평양 지역 안보 환경에 대한 설명에서 “일본 고유 영토인 북방영토와 다케시마(일본이 주장하는 독도 명칭) 영토 문제가 여전히 미해결 상태로 존재한다”고 적었다.
이로써 방위성은 2005년 이후 20년째 방위백서에서 독도 관련 억지 주장을 이어갔다. 일본은 또 방위백서 지도에서 독도를 일본 영해 안에 넣어 표시하고, 자위대 주요 부대 위치를 표시한 지도에도 독도를 다케시마로 표기했다.
한편 주변국과 관련된 기술에서 일본은 세계가 제2차 세계대전 이후 최대 시련을 맞아 ‘새로운 위기 시대’에 돌입했다고 분석하면서 “러시아의 우크라이나 침공과 같은 심각한 사태가 향후 인도·태평양 지역, 그중에서도 동아시아에서 발생할 가능성을 배제할 수 없다”고 했다.
특히 북한 핵·미사일 개발에 대해서는 작년과 마찬가지로 “우리나라(일본) 안전에 종전보다 한층 중대하고 절박한 위협”이라고 지적했다. ‘종전보다 한층’이라는 문구는 작년부터 들어갔다.
또 북한이 이미 탄도미사일에 핵무기를 탑재해 일본을 공격할 능력을 보유했으며 전술 핵무기 탑재를 염두에 두고 장거리 순항미사일 실용화를 추구하고 있다고 분석했다.
중국 군사 활동에 대해서도 지난해와 같이 “일본과 국제사회의 심각한 우려 사항이자 지금까지 없던 최대의 전략적 도전”으로 규정하고 동맹국, 뜻을 같이하는 나라와 협력해 대응해야 한다고 강조했다.
중국이 대만 주변과 남중국해에서 군사 활동을 활발히 하면서 실전 능력 향상을 도모하고 러시아와 군사 협력을 한층 강화하는 점도 우려할 만하다고 덧붙였다.
러시아와 관련해서는 “극동 방면에도 최신 장비를 배치하는 경향이 있다”며 ‘강한 국가’라는 목표를 내걸고 군사 활동을 강화하고 있다고 진단했다.
    """
            )
        )
    )
