"""
Improved ingest.py
- Adds metadata (source filename, page)
- Better chunking for aviation procedures
- Cleaner JSONL structure for RAG
"""

import os, json
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

RAW_PATH = "data/raw"
OUT_FILE = "data/processed/chunks.jsonl"


def load_pdfs():
    """Load all PDFs with metadata (source + page)."""
    docs = []
    for file in os.listdir(RAW_PATH):
        if file.lower().endswith(".pdf"):
            path = os.path.join(RAW_PATH, file)
            loader = PyPDFLoader(path)
            loaded_docs = loader.load()

            # Add source metadata
            for d in loaded_docs:
                d.metadata["source"] = file

            docs.extend(loaded_docs)
    return docs


def split_docs(docs):
    """
    Enhanced chunking for aviation documents.
    Uses structured separators to preserve checklists & procedures.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=150,
        separators=[
            "\nCHECKLIST",
            "\nPROCEDURE",
            "\nWARNING",
            "\nNOTE",
            "\n\n",
            "\n",
            " "
        ],
    )
    return splitter.split_documents(docs)


def save_chunks(chunks):
    """Save as JSONL for embedding."""
    Path(os.path.dirname(OUT_FILE)).mkdir(parents=True, exist_ok=True)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for ch in chunks:
            item = {
                "text": ch.page_content,
                "metadata": {
                    "source": ch.metadata.get("source"),
                    "page": ch.metadata.get("page")
                }
            }
            json.dump(item, f)
            f.write("\n")


if __name__ == "__main__":
    docs = load_pdfs()
    chunks = split_docs(docs)
    save_chunks(chunks)

    print(f"Saved {len(chunks)} chunks → {OUT_FILE}")
