from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

llm = ChatGroq(model=LLM_MODEL, temperature= 0.3)