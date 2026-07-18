from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from config import embeddings
from typing import Any, Dict, Optional

_thread_retriever: Dict[str, Any] = {}

def process_website(url, thread_id):

    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        if not docs:
            raise ValueError("No content could be extracted from the website.")
    except Exception as e:
        raise RuntimeError(f"Failed to load website: {e}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(splits, embedding=embeddings, persist_directory=f"website_db/{thread_id}")

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": "8", "fetch_k": "20", "lambda_mult": "0.5",},
    )

    _thread_retriever[str(thread_id)]= retriever

    return {
            "documents": len(docs),
            "chunks": len(splits),
    }


def get_website_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""

    if thread_id and thread_id in _thread_retriever:
        return _thread_retriever[thread_id]
    return None
