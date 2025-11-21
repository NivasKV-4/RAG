"""
FlightLens Evaluation Package

Provides:
- Question dataset
- RAG evaluation runner
- Metrics helpers
"""

from .test_dataset import ALL_QUESTIONS
from .eval import run_full_eval
from .metrics import summarize_results

__all__ = [
    "ALL_QUESTIONS",
    "run_full_eval",
    "summarize_results",
]
