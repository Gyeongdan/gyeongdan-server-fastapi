import os

import wikipediaapi
from dotenv import load_dotenv
from langchain.chains import LLMChain, RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers.web_research import WebResearchRetriever
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(language="en", user_agent="GyeongdanProject/1.0")

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="gpt-4")

# Initialize Chroma Vector Store without documents
vector_store = Chroma(embedding_function=embeddings)

# Setup Text Splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Initialize the OpenAI Chat Model
chat_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4")

# Initialize PromptTemplate for LLMChain
prompt_template = PromptTemplate(
    template="Q: {question}\nA:", input_variables=["question"]
)

# Initialize LLMChain
llm_chain = LLMChain(llm=chat_model, prompt=prompt_template)


# Web Research Retriever initialization with a placeholder search implementation
class PlaceholderSearch:
    def retrieve(self, query):
        return [{"content": f"Simulated search result for query: {query}"}]


search = PlaceholderSearch()

web_research_retriever = WebResearchRetriever(
    vectorstore=vector_store, llm_chain=llm_chain, search=search
)

# Create the RetrievalQAWithSourcesChain
rag_chain = RetrievalQAWithSourcesChain(
    retriever=web_research_retriever,
    llm=chat_model,
    text_splitter=text_splitter,
    vector_store=vector_store,
)


# Function to handle queries using the RAG pipeline
def query_rag(question: str):  # pylint: disable=redefined-outer-name
    # Step 1: Retrieve relevant documents from Wikipedia
    wiki_page = wiki_wiki.page(question)
    if wiki_page.exists():
        wiki_text = wiki_page.text
    else:
        wiki_text = "No relevant Wikipedia page found."

    # Step 2: Combine documents and split into chunks
    chunks = text_splitter.split_text(wiki_text)

    # Step 3: Embed and store the chunks in Chroma
    vector_store.add_texts(chunks)

    # Step 4: Retrieve relevant documents from web research
    web_docs = web_research_retriever.retrieve(question)

    # Step 5: Combine web documents and split into chunks
    for doc in web_docs:
        chunks.extend(text_splitter.split_text(doc["content"]))

    # Step 6: Use the chain to get a response
    response = rag_chain(  # pylint: disable=redefined-outer-name
        {
            "question": question,  # pylint: disable=redefined-outer-name
            "retriever_kwargs": {"k": 5},  # Number of documents to retrieve
        }
    )

    return response


# Example Usage
if __name__ == "__main__":
    question = "What is the capital of France?"
    response = query_rag(question)
    print(response)
