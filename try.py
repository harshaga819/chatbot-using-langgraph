from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os

load_dotenv()

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

print(embeddings.embed_query("Hello World"))