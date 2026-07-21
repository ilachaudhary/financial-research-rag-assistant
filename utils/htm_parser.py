from pathlib import Path
from bs4 import BeautifulSoup

# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# DATA_DIR = PROJECT_ROOT / "data"
# print(DATA_DIR)
# documents = []
#
# for file_path in DATA_DIR.rglob("*.htm"):
#     print(file_path)
#     with open(file_path, "r", encoding="utf-8") as file:
#         html_content = file.read()
#
#     soup = BeautifulSoup(html_content, "xml")
#     text_content = soup.get_text(separator="\n")
#     print("TITLE:", soup.title)
#
#
#     documents.append({
#         "file_name": file_path.name,
#         "content": html_content
#     })

"""Parse SEC 10-K .htm filings into clean, section-aware text."""
import re
from bs4 import BeautifulSoup

# Standard 10-K Item headers we try to detect for section-aware chunking
ITEM_PATTERN = re.compile(
    r"(item\s+\d+[a-c]?\.?\s*[-–—]?\s*[A-Za-z][^\n]{0,80})",
    re.IGNORECASE,
)


def load_and_clean_htm(file_path: str) -> str:
    documents = []
    """Load a 10-K .htm file and strip it down to readable plain text."""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "xml")

    # Remove non-content tags
    for tag in soup(["script", "style", "head", "meta", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Collapse excessive whitespace/newlines that HTML tables produce
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def split_into_sections(text: str):
    """
    Split full filing text into (section_title, section_text) pairs using
    'Item X' headers as boundaries. Falls back to a single 'Full Filing'
    section if no items are detected.
    """
    matches = list(ITEM_PATTERN.finditer(text))
    if not matches:
        return [("Full Filing", text)]

    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = m.group(1).strip()
        body = text[start:end].strip()
        if len(body) > 200:  # skip noise/false-positive matches
            sections.append((title, body))
    return sections or [("Full Filing", text)]


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Simple recursive-ish character chunker with overlap, splitting on
    paragraph boundaries where possible to avoid mid-sentence cuts."""
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""

    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current += para + "\n"
        else:
            if current:
                chunks.append(current.strip())
            # handle paragraphs longer than chunk_size on their own
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i:i + chunk_size])
                current = ""
            else:
                current = para + "\n"

    if current.strip():
        chunks.append(current.strip())

    # add overlap between consecutive chunks
    overlapped = []
    for i, c in enumerate(chunks):
        if i == 0:
            overlapped.append(c)
        else:
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + " " + c)
    return overlapped

#
# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# file_path = PROJECT_ROOT / "data"
# content = load_and_clean_htm(file_path)[0]["content"]
# print(chunk_text(content, 200, 10)[50])
