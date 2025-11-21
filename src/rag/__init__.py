"""
FlightLens RAG Module
Exports RAG utilities from chain.py
"""

from src.rag.chain import (
    answer_question,
    answer_question_with_sources,
)

__all__ = [
    "answer_question",
    "answer_question_with_sources",
]
