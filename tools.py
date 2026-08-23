from langchain_tavily import TavilySearch
from langchain_core.tools import tool 
import requests
import math
from dotenv import load_dotenv
import os

load_dotenv()

search_tool = TavilySearch(
    max_results = 5,
    topic = "general",
    search_depth = "deep research"
)

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