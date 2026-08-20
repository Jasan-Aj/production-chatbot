from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from typing import TypedDict

load_dotenv()

llm_model = ChatGroq(
    model = os.environ.get("GROQ_MODEL"),
    api_key= os.environ.get("GROQ_API_KEY"),
    reasoning_format = 'hidden'
)

class ChatNameState(TypedDict):
    content: str
    name: str

graph = StateGraph(ChatNameState)

def summerze_content(state: ChatNameState):
    prompt = [
        SystemMessage(content= "You are a user query summerizer, you need to create a name by summerizing the provided user query"),
        HumanMessage(content= f"Give a name for this query :{state['content']}")
    ]
    response = llm_model.invoke(prompt)
    return {'name': response.content}

graph.add_node('summerze_content', summerze_content)

graph.add_edge(START, 'summerze_content')
graph.add_edge('summerze_content', END)

summerize_agent = graph.compile()
