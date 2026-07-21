"""Tool implementations the agent can call."""
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

import config

_model = None
_index = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBED_MODEL_NAME)
    return _model


def _get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        _index = pc.Index(config.INDEX_NAME)
    return _index


def search_10k(query: str, ticker: str = None, top_k: int = 5) -> str:
    """Semantic search over ingested 10-K chunks, optionally filtered by ticker."""
    model = _get_model()
    index = _get_index()
    vector = model.encode([query], normalize_embeddings=True).tolist()[0]

    filter_dict = {"ticker": ticker.upper()} if ticker else None
    results = index.query(
        vector=vector, top_k=top_k, include_metadata=True, filter=filter_dict
    )

    if not results["matches"]:
        return "No relevant results found."

    formatted = []
    for m in results["matches"]:
        md = m["metadata"]
        formatted.append(
            f"[{md.get('ticker')} {md.get('year')} | {md.get('section')} | score={m['score']:.3f}]\n{md.get('text')}"
        )
        return "\n\n---\n\n".join(formatted)


# Tool schema for Groq / OpenAI-style function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_10k",
            "description": (
                "Search across ingested 10-K filings (Apple, Tesla, Nvidia, Microsoft) "
                "for relevant passages. Use this whenever the user asks about financial "
                "details, risk factors, business strategy, or any content from a 10-K."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query / question"},
                    "ticker": {
                        "type": "string",
                        "description": "Optional: restrict search to one company (AAPL, TSLA, NVDA, MSFT)",
                    },
                    "top_k": {"type": "integer", "description": "Number of chunks to retrieve", "default": 5},
                },
                "required": ["query"],
            },
        },
    }
]

AVAILABLE_FUNCTIONS = {"search_10k": search_10k}