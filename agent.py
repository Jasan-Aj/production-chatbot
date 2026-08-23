from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from tools import search_tool, get_stock_price, get_weather, calculator

load_dotenv()

connection = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(connection)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm_model = ChatGroq(
    api_key= os.environ.get("GROQ_API_KEY"),
    model= os.environ.get("GROQ_MODEL"),
    reasoning_format="hidden"
)

tools = [search_tool, get_stock_price, get_weather, calculator]

llm_with_tools = llm_model.bind_tools(tools)

graph = StateGraph(ChatState)

def chat_node(state: ChatState):
    prompt = state['messages']
    response = llm_with_tools.invoke(prompt)

    return {"messages":[response]}

tool_node = ToolNode(tools)

graph.add_node("chat_node",chat_node) 
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tool_node", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

def get_threads():
    all_threads = set()
    
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return [{'thread_id': tid, 'name': None} for tid in all_threads]