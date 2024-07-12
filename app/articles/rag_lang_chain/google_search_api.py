import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.retrievers.web_research import WebResearchRetriever
from langchain_community.vectorstores import Chroma
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 환경 변수 로드
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_AGENT = os.getenv("USER_AGENT", "gyeongdanproject")

# 벡터 스토어 설정
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
    persist_directory="./chroma_db_oai",
)

# LLM 설정
search_llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# Google 검색 API 래퍼 설정
search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID
)

# Web Research Retriever 설정
web_research_retriever = WebResearchRetriever.from_llm(
    vectorstore=vectorstore,
    llm=search_llm,
    search=search,
)

# QA 체인 설정
response_llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.9)
qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
    response_llm, retriever=web_research_retriever
)


def perform_search(query):
    try:
        result = qa_chain({"question": query})
        return result
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}")
        return None


def main():
    user_input = "저금리대출이 뭐야?"
    result = perform_search(user_input)
    if result:
        print(result)


if __name__ == "__main__":
    main()
