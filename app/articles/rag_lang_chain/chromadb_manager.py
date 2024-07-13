import os
from typing import List

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()


class ChromaDBManager:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        self.vectorstore = Chroma(
            collection_name="documents", embedding_function=self.embeddings
        )

    def add_documents(self, documents: List[dict]):
        texts = [doc["snippet"] for doc in documents]
        metadata = [{"id": doc["link"], "title": doc["title"]} for doc in documents]
        self.vectorstore.add_texts(texts, metadata)

    def search_documents(self, query: str, k: int = 5) -> list[Document]:
        query_vector = self.embeddings.embed_query(query)
        results = self.vectorstore.similarity_search_by_vector(query_vector, k=k)
        return results
