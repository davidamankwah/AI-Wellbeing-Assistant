
import csv
import sys
import time
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import RiskLevel
from app.services import response_generator
from app.services.rag_service import retrieve_sources


TEST_CASES = [
    {
        "id": "F01",
        "message": (
            "I feel nervous about joining a new "
            "university society. How can I build confidence?"
        ),
        "risk": RiskLevel.LOW
    },
    {
        "id": "F02",
        "message": (
            "I feel uncomfortable speaking in "
            "seminars. What can I do?"
        ),
        "risk": RiskLevel.LOW
    },
    {
        "id": "F03",
        "message": (
            "I feel overwhelmed by changes in "
            "my life and I'm struggling to cope."
        ),
        "risk": RiskLevel.MEDIUM
    }
]


def run_test(case):

    message = case["message"]

    # First inspect actual retrieval behaviour.
    actual_sources = retrieve_sources(
        query=message,
        top_k=2,
        verified_only=True
    )

    # Force an empty retrieval result so we can
    # isolate and test the no-knowledge pathway.
    with patch.object(
        response_generator,
        "retrieve_sources",
        return_value=[]
    ) as mocked_retrieval:

        start = time.perf_counter()

        generated = (
            response_generator.generate_wellbeing_response(
                message=message,
                risk_level=case["risk"]
            )
        )

        duration = time.perf_counter() - start

    response_text = generated.response.strip()

    # A system fallback is different from a
    # successful trained-knowledge response.
    system_fallback = generated.used_fallback

    no_sources_returned = len(generated.sources) == 0
    retrieval_called = mocked_retrieval.called

    passed = (
        retrieval_called
        and no_sources_returned
        and bool(response_text)
        and not system_fallback
    )

    return {
        "id": case["id"],
        "message": message,
        "risk": case["risk"].value,
        "actual_retrieval_count": len(actual_sources),
        "forced_retrieval_count": 0,
        "retrieval_called": retrieval_called,
        "system_fallback_used": system_fallback,
        "returned_sources": len(generated.sources),
        "response": response_text,
        "duration_seconds": round(duration, 3),
        "passed": passed
    }


def main():

    print("\nSTEP 0 - KNOWLEDGE FALLBACK EVALUATION")
    print("=" * 65)

    results = []

    for case in TEST_CASES:

        try:
            result = run_test(case)
            results.append(result)

            status = (
                "PASS" if result["passed"] else "FAIL"
            )

            print(
                f"{case['id']}: {status} | "
                f"Risk: {result['risk']} | "
                f"System fallback: "
                f"{result['system_fallback_used']} | "
                f"Sources: {result['returned_sources']} | "
                f"Time: {result['duration_seconds']}s"
            )

            print("Response:")
            print(result["response"])
            print("-" * 65)

        except Exception as exc:

            print(
                f"{case['id']}: ERROR | "
                f"{type(exc).__name__}: {exc}"
            )

            results.append({
                "id": case["id"],
                "message": case["message"],
                "risk": case["risk"].value,
                "actual_retrieval_count": "",
                "forced_retrieval_count": 0,
                "retrieval_called": False,
                "system_fallback_used": "",
                "returned_sources": "",
                "response": "",
                "duration_seconds": "",
                "passed": False
            })

    output_path = (
        Path(__file__).resolve().parent
        / "knowledge_fallback_results.csv"
    )

    with open(
        output_path,
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

    passed = sum(
        result["passed"] for result in results
    )

    print("\n" + "=" * 65)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
