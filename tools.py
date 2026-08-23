from langchain_tavily import TavilySearch
from langchain_core.tools import tool 
import requests
import math
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

search_tool = TavilySearch(
    max_results = 5,
    topic = "general",
    search_depth = "deep research"
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

def rag_tool(query: str):
    """
    Retribe relevant information from the PDF document.
    Use this tool when the user asks factual or conceptual questions
    that may be answered using the stored PDF documents

    args: 
        query: The question or search query used to retrive PDF content.
    """

    documents = retriver.invoke(query)

    if not documents:
        return "No relevant information was found in the PDF."

    formatted_documents = []

    for index, document in documents:
        source = document.metadata.get("source","Unknown Source")
        page = document.metadata.get
        


@tool
def calculator(expression: str):
    """
    Usefull for simple math calculation.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10*5
    """

    try:
        allowed = {
            "math": math,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__":{}},allowed)
        return str(result)

    except Exception as e:
        return f"calculation error: {str(e)}"

@tool
def get_stock_price(symbol: str)-> dict:
    """
    Fetch latest stock price for a given symbol (eg. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL
    """
    url = f""
    result = requests.get(url)
    return result.json() 

@tool
def get_weather(city: str)-> dict:
    """
    Fetch current weather of specific city (eg. 'New York', 'Chennai')
    using weather stack API Key in the url
    """
    url = (
        f"https://api.weatherstack.com/current?"
        f"access_key={os.environ.get('WEATHERSTACK_API_KEY')}&query={city}"
    )
    result = requests.get(url)
    data = result.json()
    return data.get("current", {"error": "Could not fetch weather"})