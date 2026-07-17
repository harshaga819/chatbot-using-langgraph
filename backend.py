from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver, sqlite3
from langchain_core.messages import BaseMessage, HumanMessage
from tools import get_stock_price, calculator, search_tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"


llm = ChatGroq(
    model=LLM_MODEL,
    temperature=0.3
)

tools= [get_stock_price, calculator, search_tool]
llm_with_tools= llm.bind_tools(tools)

class state(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

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
builder.add_edge("chat", END)


chat_reply = builder.compile(checkpointer = checkpointer)


def retrive_old_chats():
    threads= set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config['configurable']['thread_id'])
    return list(threads)
