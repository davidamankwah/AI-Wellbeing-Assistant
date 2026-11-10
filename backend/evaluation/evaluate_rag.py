
import csv
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.rag_service import retrieve_sources


EVALUATION_DIR = Path(__file__).resolve().parent

DATASET_PATH = EVALUATION_DIR / "rag_cases.json"
RESULTS_PATH = EVALUATION_DIR / "rag_results.csv"

TOP_K = 2


def is_relevant(source_title, expected_keywords):
    title = source_title.lower()

    return any(
        keyword.lower() in title
        for keyword in expected_keywords
    )


def run_evaluation():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    results = []

    hit_scores = []
    precision_scores = []
    reciprocal_ranks = []

    negative_correct = 0
    negative_total = 0

    print("\nSTAGE 8C - RAG RETRIEVAL EVALUATION")
    print("=" * 65)

    for case in cases:

        case_id = case["id"]
        message = case["message"]
        expected = case["expected_keywords"]

        retrieved = retrieve_sources(
            query=message,
            top_k=TOP_K,
            verified_only=True
        )

        titles = [source.title for source in retrieved]

        relevant_flags = [
            is_relevant(title, expected)
            for title in titles
        ]

        relevant_count = sum(relevant_flags)

        if expected:

            hit = 1 if relevant_count > 0 else 0

            # Precision@2 uses a fixed denominator.
            precision = relevant_count / TOP_K

            reciprocal_rank = 0.0

            for rank, relevant in enumerate(
                relevant_flags,
                start=1
            ):
                if relevant:
                    reciprocal_rank = 1 / rank
                    break

            hit_scores.append(hit)
            precision_scores.append(precision)
            reciprocal_ranks.append(reciprocal_rank)

            passed = bool(hit)

        else:

            negative_total += 1

            passed = len(retrieved) == 0

            if passed:
                negative_correct += 1

            hit = None
            precision = None
            reciprocal_rank = None

        results.append({
            "id": case_id,
            "message": message,
            "expected_keywords": ", ".join(expected),
            "retrieved_titles": " | ".join(titles),
            "hit_at_2": hit,
            "precision_at_2": precision,
            "reciprocal_rank": reciprocal_rank,
            "passed": passed
        })

        print(
            f"{case_id}: "
            f'{"PASS" if passed else "FAIL"} | '
            f"Retrieved: {titles}"
        )

    def average(values):
        return sum(values) / len(values) if values else 0

    hit_rate = average(hit_scores) * 100
    precision_at_2 = average(precision_scores) * 100
    mrr = average(reciprocal_ranks)

    negative_accuracy = (
        negative_correct / negative_total * 100
        if negative_total else 0
    )

    with open(
        RESULTS_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 65)
    print(f"Total test cases: {len(cases)}")
    print(f"Positive queries: {len(hit_scores)}")
    print(f"Negative queries: {negative_total}")
    print(f"Hit Rate@2: {hit_rate:.1f}%")
    print(f"Precision@2: {precision_at_2:.1f}%")
    print(f"MRR: {mrr:.3f}")
    print(
        f"Negative query accuracy: "
        f"{negative_accuracy:.1f}%"
    )
    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()
