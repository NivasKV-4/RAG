"""
Evaluation metrics for FlightLens

Provides:
- text normalization
- token-level F1
- exact match
- length ratio
- summary helpers
"""

import re
from typing import Dict, List, Tuple


def normalize(text: str) -> str:
    """Lowercase, remove extra spaces and simple punctuation."""
    if text is None:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return normalize(text).split()


def token_f1(pred: str, ref: str) -> float:
    """Simple F1 over token overlap."""
    pred_tokens = tokenize(pred)
    ref_tokens = tokenize(ref)

    if not pred_tokens or not ref_tokens:
        return 0.0

    pred_set = set(pred_tokens)
    ref_set = set(ref_tokens)
    overlap = pred_set.intersection(ref_set)

    if not overlap:
        return 0.0

    precision = len(overlap) / len(pred_set)
    recall = len(overlap) / len(ref_set)
    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def exact_match(pred: str, ref: str) -> bool:
    """Strict normalized string equality."""
    return normalize(pred) == normalize(ref)


def length_ratio(pred: str, ref: str) -> float:
    """Ratio of predicted length to reference length."""
    pred_len = len(tokenize(pred))
    ref_len = len(tokenize(ref))
    if ref_len == 0:
        return 0.0
    return pred_len / ref_len


def evaluate_pair(pred: str, ref: str) -> Dict[str, float]:
    """Compute all metrics for a single prediction-reference pair."""
    return {
        "f1": token_f1(pred, ref),
        "exact_match": 1.0 if exact_match(pred, ref) else 0.0,
        "length_ratio": length_ratio(pred, ref),
    }


def summarize_results(records: List[Dict]) -> Dict[str, float]:
    """
    Aggregate metrics across all records.
    Expects each record to include keys: 'f1', 'exact_match', 'length_ratio'.
    """
    if not records:
        return {"f1": 0.0, "exact_match": 0.0, "length_ratio": 0.0}

    def avg(key: str) -> float:
        vals = [r.get(key, 0.0) for r in records]
        return sum(vals) / max(len(vals), 1)

    return {
        "f1": avg("f1"),
        "exact_match": avg("exact_match"),
        "length_ratio": avg("length_ratio"),
    }
