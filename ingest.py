"""
Ingest a 10-K .htm filing: parse -> section-split -> chunk -> embed -> upsert to Pinecone.

Usage:
    python ingest.py --file data/AAPL_2024_10K.htm --ticker AAPL --year 2024
"""
import argparse
import uuid
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

import config
from utils.htm_parser import load_and_clean_htm, split_into_sections, chunk_text


def get_or_create_index(pc: Pinecone):
    existing = [i["name"] for i in pc.list_indexes()]
    if config.INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{config.INDEX_NAME}'...")
        pc.create_index(
            name=config.INDEX_NAME,
            dimension=config.EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(config.INDEX_NAME)


def ingest(filepath: str, ticker: str, year: str):
    print(f"Loading {filepath} ...")
    text = load_and_clean_htm(filepath)
    sections = split_into_sections(text)
    print(f"Found {len(sections)} sections.")

    model = SentenceTransformer(config.EMBED_MODEL_NAME)
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    index = get_or_create_index(pc)

    all_chunks = []
    for title, body in sections:
        for chunk in chunk_text(body, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
            all_chunks.append({"section": title, "text": chunk})

    print(f"Total chunks to embed: {len(all_chunks)}")

    batch_size = 64
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding+Upserting"):
        batch = all_chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()

        vectors = []
        for c, emb in zip(batch, embeddings):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": emb,
                "metadata": {
                    "ticker": ticker.upper(),
                    "year": str(year),
                    "section": c["section"][:100],
                    "text": c["text"][:2000],  # keep metadata payload reasonable
                },
            })
        index.upsert(vectors=vectors)

    print(f"Done. Ingested {ticker.upper()} {year} 10-K into Pinecone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to .htm 10-K filing")
    parser.add_argument("--ticker", required=True, help="e.g. AAPL, TSLA, NVDA, MSFT")
    parser.add_argument("--year", required=True, help="Fiscal year of the filing")
    args = parser.parse_args()
    ingest(args.file, args.ticker, args.year)