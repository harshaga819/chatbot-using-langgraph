from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests
import os
from typing import Dict, Optional
from retriever_manager import get_retriever 
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState


search= DuckDuckGoSearchRun(region="us-en")

@tool
def search_tool(query: str) -> str:
    """
    Search the web.
    """
    try:
        return search.run(query)
    except Exception as e:
        return f"Search failed: {str(e)}"
    


@tool
def rag_tool(query: str, state: Annotated[dict, InjectedState]) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Always include the thread_id when calling this tool.
    """
    thread_id = state["thread_id"]
    retriever = get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]

    return {
        "query": query,
        "context": context,
    }



@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    apikey = os.getenv("ALPHAVANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}"
    r = requests.get(url)
    return r.json()