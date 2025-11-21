"""
FlightLens Data Processing Package
Document ingestion, chunking, and FAISS embedding generation
"""

from src.data.ingest import (
    load_pdfs,
    split_docs,
    save_chunks
)

from src.data.embed_faiss import (
    load_chunks
)

__all__ = [
    # Ingestion functions
    'load_pdfs',
    'split_docs',
    'save_chunks',
    # Embedding functions
    'load_chunks'
]
