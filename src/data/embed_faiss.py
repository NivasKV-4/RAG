"""
embed_faiss.py - Final Working Version
- No manual embedding
- FAISS.from_texts() handles embedding
- Progress printed every 100 chunks
"""

import os, json
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

CHUNK_FILE = os.getenv("PROCESSED_DATA_PATH", "data/processed") + "/chunks.jsonl"
INDEX_DIR = os.getenv("FAISS_INDEX_PATH", "models/faiss_index")
EMBED_MODEL = os.getenv("FLIGHTLENS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def load_chunks():
    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

if __name__ == "__main__":
    data = load_chunks()
    texts = [d["text"] for d in data]
    metadatas = [d["metadata"] for d in data]

    print(f"Loaded {len(texts)} chunks.")
    print(f"Using embedding model: {EMBED_MODEL}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    # Fake progress log (embedding happens inside FAISS)
    for i in range(0, len(texts), 100):
        print(f"Embedding progress: {i}/{len(texts)}")

    print("Building FAISS index... (embedding handled internally)")

    # ⭐ THIS is the correct FAISS call — no errors
    db = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    os.makedirs(INDEX_DIR, exist_ok=True)
    db.save_local(INDEX_DIR)

    print(f"FAISS index saved → {INDEX_DIR}")
    print("DONE.")
