"""
FlightLens Evaluation Runner
Compatible with your actual evaluation codebase.
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# FIX PYTHONPATH
# ---------------------------------------------------------
project_root = Path(__file__).resolve().parents[2]
src_root = project_root / "src"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

# ---------------------------------------------------------
# IMPORTS (MATCH YOUR REAL FILES)
# ---------------------------------------------------------
from src.evaluate.test_dataset import ALL_QUESTIONS
from src.evaluate.metrics import summarize_results, evaluate_pair
from src.evaluate.baselines import run_bm25_baseline
from src.rag.chain import answer_question


# ---------------------------------------------------------
# RAG EVALUATION
# ---------------------------------------------------------
def run_rag_eval():
    results = []

    print("\n==========================================")
    print(" Evaluating FlightLens RAG System")
    print("==========================================\n")
    print(f"Total questions: {len(ALL_QUESTIONS)}\n")

    for i, item in enumerate(ALL_QUESTIONS, 1):

        qid = item["id"]
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"[{i}/{len(ALL_QUESTIONS)}] {qid}: {question[:70]}")

        try:
            answer = answer_question(question)
        except Exception as e:
            answer = f"[ERROR] {e}"

        m = evaluate_pair(answer, ground_truth)

        results.append({
            "id": qid,
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "category": item["category"],
            "difficulty": item["difficulty"],
            "requires_context": ",".join(item.get("requires_context", [])),
            "f1": m["f1"],
            "exact_match": m["exact_match"],
            "length_ratio": m["length_ratio"],
        })

    return results


# ---------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------
def save_results(rag_results, bm25_results, output_dir):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    with open(output_dir / f"rag_results_{timestamp}.json", "w") as f:
        json.dump(rag_results, f, indent=2)

    with open(output_dir / f"bm25_results_{timestamp}.json", "w") as f:
        json.dump(bm25_results, f, indent=2)

    # CSV
    pd.DataFrame(rag_results).to_csv(output_dir / f"rag_results_{timestamp}.csv", index=False)
    pd.DataFrame(bm25_results).to_csv(output_dir / f"bm25_results_{timestamp}.csv", index=False)

    # Summary
    rag_summary = summarize_results(rag_results)
    bm25_summary = summarize_results(bm25_results)

    summary = {
        "rag": rag_summary,
        "bm25": bm25_summary,
        "total_questions": len(rag_results)
    }

    with open(output_dir / f"summary_{timestamp}.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n======================================")
    print(" Evaluation Complete")
    print("======================================")
    print(f"Results saved in: {output_dir}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    output_dir = project_root / "evaluation" / "results"

    print("\nRunning RAG evaluation...")
    rag_results = run_rag_eval()

    print("\nRunning BM25 baseline evaluation...")
    bm25_results = run_bm25_baseline(ALL_QUESTIONS)

    save_results(rag_results, bm25_results, output_dir)
