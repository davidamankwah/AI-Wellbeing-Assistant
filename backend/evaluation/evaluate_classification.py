
import csv
import json
import sys
import time
from pathlib import Path

# Allow imports from the backend/app directory
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.input_validator import validate_message
from app.services.risk_level import classify_message
from app.services.response_controller import control_response


EVALUATION_DIR = Path(__file__).resolve().parent

DATASET_PATH = EVALUATION_DIR / "classification_cases.json"
RESULTS_PATH = EVALUATION_DIR / "classification_results.csv"


def run_evaluation():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    results = []

    print("\nSTAGE 8A - CLASSIFICATION EVALUATION")
    print("=" * 60)

    for case in cases:
        case_id = case["id"]
        message = case["message"]

        expected_risk = case["expected_risk"]
        expected_route = case["expected_route"]

        start_time = time.perf_counter()

        actual_risk = "ERROR"
        actual_route = "ERROR"
        error = ""

        try:
            validation = validate_message(message)

            if not validation.valid:
                raise ValueError(
                    f"Input validation failed: {validation.error}"
                )

            classification = classify_message(validation)
            decision = control_response(classification)

            actual_risk = classification.safeguarding_risk.value
            actual_route = decision.route.value

        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        elapsed = round(time.perf_counter() - start_time, 3)

        risk_correct = actual_risk == expected_risk
        route_correct = actual_route == expected_route

        results.append({
            "id": case_id,
            "message": message,
            "expected_risk": expected_risk,
            "actual_risk": actual_risk,
            "risk_correct": risk_correct,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_correct": route_correct,
            "duration_seconds": elapsed,
            "error": error
        })

        result = "PASS" if route_correct else "FAIL"

        print(
            f"{case_id}: {result} | "
            f"Risk: {actual_risk} | "
            f"Route: {actual_route} | "
            f"Time: {elapsed}s"
        )

    total = len(results)

    risk_passed = sum(
        result["risk_correct"] for result in results
    )

    route_passed = sum(
        result["route_correct"] for result in results
    )

    risk_accuracy = (risk_passed / total) * 100 if total else 0
    route_accuracy = (route_passed / total) * 100 if total else 0

    print("\n" + "=" * 60)
    print(f"Total test cases: {total}")
    print(f"Risk accuracy: {risk_accuracy:.1f}%")
    print(f"Routing accuracy: {route_accuracy:.1f}%")

    with open(
        RESULTS_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "message",
                "expected_risk",
                "actual_risk",
                "risk_correct",
                "expected_route",
                "actual_route",
                "route_correct",
                "duration_seconds",
                "error"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()
