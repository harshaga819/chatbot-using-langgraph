import os
import tempfile
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from typing import Any, Dict, Optional

load_dotenv()

_thread_retriever: Dict[str, Any] = {}

embeddings = HuggingFaceEmbeddings(model_name= "sentence-transformers/all-MiniLM-L6-v2")

def upload_file(file_bytes: bytes, thread_id: str, filename: Optional[str]= None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.

    Returns a summary dict that can be surfaced in the UI.
    """

    if not file_bytes:
        raise ValueError("No Byte received")
    
    # Here we are creating a new temp file with same data as uploaded file this is done because PyPDFLoader
    # does not takes the bytes directly it takes the file path and from there it takes the data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path= temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)

        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _thread_retriever[str(thread_id)]= retriever

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

def get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""

    if thread_id and thread_id in _thread_retriever:
        return _thread_retriever[thread_id]
    return None