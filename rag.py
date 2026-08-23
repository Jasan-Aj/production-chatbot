import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

llm_model = ChatGroq(
    api_key= os.environ.get("GROQ_API_KEY"),
    model= os.environ.get("GROQ_MODEL"),
    reasoning_format="hidden"
)

loader = PyPDFLoader("Week.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(
    model= os.environ.get("GEMINI_EMBEDDING_MODEL")
)

vector_store = FAISS.from_documents(chunks, embeddings)

retriver = vector_store.as_retriever(search_type="similarity", search_kwargs = {'k':4})

response = retriver.invoke("chatbots applications")
print(response)





