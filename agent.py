from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

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

graph = StateGraph(ChatState)

def invoke_chat(state: ChatState):
    prompt = state['messages']
    response = llm_model.invoke(prompt)

    return {"messages":[response]}

graph.add_node("invoke_chat",invoke_chat)

graph.add_edge(START, "invoke_chat")
graph.add_edge("invoke_chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

def get_threads():
    all_threads = set()
    
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return [{'thread_id': tid, 'name': None} for tid in all_threads]