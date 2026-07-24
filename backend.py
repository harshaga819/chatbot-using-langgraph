from dotenv import load_dotenv
from config import llm
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver, sqlite3
from langchain_core.messages import BaseMessage, HumanMessage
from tools import get_stock_price, rag_tool, search_tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

tools= [get_stock_price, rag_tool, search_tool]
llm_with_tools= llm.bind_tools(tools)

class state(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]
    thread_id : str

def chat(state):
    message = state["messages"]
    response = llm_with_tools.invoke(message)
    return {"messages":[response]}

tool_node= ToolNode(tools)

conn= sqlite3.connect(database= 'chatbot_database.db', check_same_thread= False)
checkpointer = SqliteSaver(conn= conn)

builder = StateGraph(state)

builder.add_node("chat", chat)
builder.add_node("tools", tool_node)

builder.add_edge(START, "chat")
builder.add_conditional_edges("chat",tools_condition)
builder.add_edge('tools', 'chat')



chat_reply = builder.compile(checkpointer = checkpointer)


def retrive_old_chats():
    threads= set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config['configurable']['thread_id'])
    return list(threads)
