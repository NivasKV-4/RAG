"""
Core evaluation logic for FlightLens RAG.

- Loads RAG answer function
- Runs over ALL_QUESTIONS
- Computes metrics per question
"""

import sys
from pathlib import Path
from typing import List, Dict

# Ensure project root in sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.chain import answer_question
from evaluate.test_dataset import ALL_QUESTIONS
from evaluate.metrics import evaluate_pair


def run_full_eval() -> List[Dict]:
    """
    Run evaluation over ALL_QUESTIONS using the current RAG pipeline.

    Returns:
        List of result dicts, each including:
        - id, question, ground_truth
        - answer
        - category, difficulty, requires_context
        - f1, exact_match, length_ratio
    """
    results: List[Dict] = []

    for q in ALL_QUESTIONS:
        qid = q["id"]
        question = q["question"]
        gt = q["ground_truth"]
        category = q.get("category", "unknown")
        difficulty = q.get("difficulty", "unknown")
        requires_context = q.get("requires_context", [])

        # For now, we do NOT inject METAR/telemetry, but we keep the annotation.
        try:
            answer = answer_question(question)
        except Exception as e:
            answer = f"[ERROR during answer generation: {e}]"

        m = evaluate_pair(answer, gt)

        record = {
            "id": qid,
            "question": question,
            "ground_truth": gt,
            "answer": answer,
            "category": category,
            "difficulty": difficulty,
            "requires_context": ",".join(requires_context),
            "f1": m["f1"],
            "exact_match": m["exact_match"],
            "length_ratio": m["length_ratio"],
        }
        results.append(record)

    return results


if __name__ == "__main__":
    from evaluate.metrics import summarize_results

    print("Running FlightLens RAG evaluation over dataset...")
    records = run_full_eval()
    summary = summarize_results(records)

    print("\nSummary Metrics:")
    print(f"  F1:          {summary['f1']:.3f}")
    print(f"  Exact Match: {summary['exact_match']:.3f}")
    print(f"  Len Ratio:   {summary['length_ratio']:.3f}")
    print(f"\nTotal questions: {len(records)}")
