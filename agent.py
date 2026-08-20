from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

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

chatbot = graph.compile(MemorySaver())
