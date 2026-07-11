import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Import your tools
from app.tools.order_tool import get_order_status, update_order_status, search_knowledge_base

# 1. Setup Tools
tools = [get_order_status, update_order_status, search_knowledge_base]

# 2. Setup LLM (Using Groq/Llama as your primary model)
llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    api_key=os.getenv("GROQ_API_KEY")
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define System Prompt
SYSTEM_INSTRUCTIONS = """
You are a helpful company support assistant.
1. Use 'search_knowledge_base' to find information from uploaded policy documents.
2. Use 'get_order_status' or 'update_order_status' whenever the user asks about an order status or wants to update an order.
3. For order requests, do not ask for confirmation or follow the generic SOP script; use the available order tools directly.
4. If the tool returns information, use it to synthesize a helpful, conversational answer.
5. If the tool returns information that is related but not an exact match, explain what you found and how it might relate.
6. If you absolutely cannot find the answer, be honest and ask the user to rephrase their request.
"""

# 4. Define State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 5. Define Agent Node
def agent_node(state: State):
    # Inject the system prompt into the messages list every time
    system_message = SystemMessage(content=SYSTEM_INSTRUCTIONS)
    # Ensure system prompt is at the start, followed by history
    messages = [system_message] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 6. Build the Graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# Compile
graph = builder.compile()