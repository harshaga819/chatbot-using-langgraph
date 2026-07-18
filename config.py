from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_groq import ChatGroq
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Project Paths

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"

# Model Configuration

LLM_MODEL = "llama-3.3-70b-versatile"

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)


llm = ChatGroq(
    model=LLM_MODEL,
    temperature= 0.3
)