# 📊 Financial Research RAG Assistant

An agentic AI research assistant that answers questions about company 10-K filings (Apple, Tesla, Nvidia, Microsoft) 
using Retrieval-Augmented Generation. It parses SEC 10-K `.htm` filings, chunks and embeds them locally,
stores vectors in Pinecone, and uses an LLM agent (via Groq) 
with tool-calling to retrieve and reason over the filings in an interactive chat.

---

## Features

- Parses raw SEC `.htm` 10-K filings and strips them to clean text
- Section-aware chunking (splits on `Item 1`, `Item 1A`, `Item 7`, etc.)
- Local, free embedding generation — no OpenAI key needed
- Semantic search over filings via Pinecone, filterable by ticker
- Interactive CLI agent that decides when to search and cites its sources

---

## Project Structure

```
financial-research-rag-assistant/
├── ingest.py            # Parse, chunk, embed, and upsert a 10-K filing
├── agent.py              # Interactive agentic CLI
├── tools.py               # Tool definitions used by the agent
├── config.py              # Configuration and environment loading
├── utils/
│   └── htm_parser.py      # HTML parsing, section splitting, chunking
├── data/                   # Place your .htm 10-K filings here (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone and create a virtual environment
```bash
git clone https://github.com/<your-username>/financial-research-rag-assistant.git
cd financial-research-rag-assistant
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get free API keys

| Service | Purpose | Link |
|---|---|---|
| Pinecone | Vector storage | https://www.pinecone.io/ 
| Groq | LLM reasoning + tool-calling | https://console.groq.com/

### 4. Configure environment variables
```
Edit `.env` and add your real keys :
```
PINECONE_API_KEY=pcsk_your_real_key
GROQ_API_KEY=gsk_your_real_key
```

### 5. Add your filings
Download 10-K `.htm` filings from [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar) and place them in `data/`, e.g.:
```
data/AAPL_2024_10K.htm
data/TSLA_2024_10K.htm
data/NVDA_2024_10K.htm
data/MSFT_2024_10K.htm

---

### Run the interactive agent
```bash
python agent.py
```

Example questions:
```
> What does Apple say about supply chain risk?
> Compare Tesla's and Nvidia's R&D spending discussion.
> Summarize Microsoft's cloud business strategy from the latest 10-K.
```

---

## How It Works

1. **Parse** — `utils/htm_parser.py` strips HTML tags/scripts and extracts clean text from the raw SEC filing.
2. **Chunk** — Text is split by 10-K `Item` sections, then further chunked (~1000 chars, 150-char overlap) to stay within embedding context limits.
3. **Embed** — Each chunk is embedded locally using `BAAI/bge-small-en-v1.5` (384-dim, free, runs on CPU).
4. **Store** — Vectors are upserted to a Pinecone serverless index with metadata (`ticker`, `year`, `section`, `text`).
5. **Retrieve + Reason** — The agent (Groq/Llama 3.3 70B) receives a `search_10k` tool it can call with a query and optional ticker filter, retrieves relevant chunks, and generates a cited answer.

---

## Roadmap / Ideas

- [ ] Multi-company comparison tool (parallel `search_10k` calls across tickers)
- [ ] Filter search by specific `Item` section
- [ ] Persistent chat history across sessions
- [ ] Web UI (Streamlit/Gradio) instead of CLI

---

## License

MIT — feel free to fork and adapt.

## Disclaimer

This project is for research and educational purposes only. 
It is not financial advice. Always verify figures against the original SEC filings.