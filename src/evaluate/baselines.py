"""
Baseline Comparisons for FlightLens

Provides a simple BM25 retrieval baseline using the chunked documents.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

from evaluate.metrics import evaluate_pair

load_dotenv()

project_root = Path(__file__).parent.parent
CHUNK_FILE = Path(os.getenv("PROCESSED_DATA_PATH", "data/processed")) / "chunks.jsonl"


class BM25RetrievalBaseline:
    """BM25 over preprocessed chunks.jsonl"""

    def __init__(self, chunk_file: Path = CHUNK_FILE):
        self.chunk_file = chunk_file
        self.texts: List[str] = []
        self.tokenized_texts: List[List[str]] = []
        self.bm25 = None

    def load_corpus(self):
        if not self.chunk_file.exists():
            raise FileNotFoundError(f"Chunk file not found: {self.chunk_file}")
        with open(self.chunk_file, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                self.texts.append(obj["text"])
        self.tokenized_texts = [t.lower().split() for t in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_texts)

    def answer_question(self, question: str, k: int = 3) -> str:
        if self.bm25 is None:
            self.load_corpus()
        query_tokens = question.lower().split()
        scores = self.bm25.get_top_n(query_tokens, self.texts, n=k)
        # Baseline answer = concatenation of top chunks
        return "\n\n".join(scores)


def run_bm25_baseline(questions: List[Dict]) -> List[Dict]:
    """
    Run BM25 baseline on given question structs:
    Each question dict should have keys: id, question, ground_truth.
    """
    bm = BM25RetrievalBaseline()
    bm.load_corpus()

    results = []
    for q in questions:
        qid = q["id"]
        question = q["question"]
        gt = q["ground_truth"]

        answer = bm.answer_question(question)
        m = evaluate_pair(answer, gt)

        results.append({
            "id": qid,
            "question": question,
            "ground_truth": gt,
            "answer": answer,
            "f1": m["f1"],
            "exact_match": m["exact_match"],
            "length_ratio": m["length_ratio"],
        })
    return results


if __name__ == "__main__":
    from evaluate.test_dataset import ALL_QUESTIONS
    from evaluate.metrics import summarize_results

    print("Running BM25 baseline over evaluation dataset...")
    records = run_bm25_baseline(ALL_QUESTIONS)
    summary = summarize_results(records)

    print("\nBaseline Summary Metrics:")
    print(f"  F1:          {summary['f1']:.3f}")
    print(f"  Exact Match: {summary['exact_match']:.3f}")
    print(f"  Len Ratio:   {summary['length_ratio']:.3f}")
    print(f"\nTotal questions: {len(records)}")
