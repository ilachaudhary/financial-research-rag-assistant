import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

INDEX_NAME = "10k-filings"
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"   # free, local, 384-dim
EMBED_DIM = 384
GROQ_MODEL = "llama-3.3-70b-versatile"        # free tier on Groq

CHUNK_SIZE = 1000       # characters
CHUNK_OVERLAP = 150

COMPANIES = ["AAPL", "TSLA", "NVDA", "MSFT"]