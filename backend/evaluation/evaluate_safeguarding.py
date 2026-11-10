
import csv
import sys
from pathlib import Path

# Allow imports from the backend directory
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import MessageClassification, RiskLevel
from app.services.response_controller import (
    ResponseRoute,
    control_response
)


EVALUATION_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EVALUATION_DIR / "safeguarding_results.csv"


# Synthetic classification cases.
# These test controller logic, not LLM accuracy.
TEST_CASES = [
    {
        "id": "S01",
        "name": "LOW wellbeing",
        "risk": RiskLevel.LOW,
        "scope": True,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.LOW
    },
    {
        "id": "S02",
        "name": "MEDIUM distress",
        "risk": RiskLevel.MEDIUM,
        "scope": True,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.MEDIUM
    },
    {
        "id": "S03",
        "name": "HIGH risk",
        "risk": RiskLevel.HIGH,
        "scope": True,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.HIGH
    },
    {
        "id": "S04",
        "name": "LOW clinical request",
        "risk": RiskLevel.LOW,
        "scope": True,
        "clinical": True,
        "injection": False,
        "expected": ResponseRoute.CLINICAL
    },
    {
        "id": "S05",
        "name": "MEDIUM clinical request",
        "risk": RiskLevel.MEDIUM,
        "scope": True,
        "clinical": True,
        "injection": False,
        "expected": ResponseRoute.CLINICAL
    },
    {
        "id": "S06",
        "name": "HIGH clinical request",
        "risk": RiskLevel.HIGH,
        "scope": True,
        "clinical": True,
        "injection": False,
        "expected": ResponseRoute.HIGH
    },
    {
        "id": "S07",
        "name": "LOW injection",
        "risk": RiskLevel.LOW,
        "scope": True,
        "clinical": False,
        "injection": True,
        "expected": ResponseRoute.INJECTION
    },
    {
        "id": "S08",
        "name": "MEDIUM injection",
        "risk": RiskLevel.MEDIUM,
        "scope": True,
        "clinical": False,
        "injection": True,
        "expected": ResponseRoute.INJECTION
    },
    {
        "id": "S09",
        "name": "HIGH injection",
        "risk": RiskLevel.HIGH,
        "scope": True,
        "clinical": False,
        "injection": True,
        "expected": ResponseRoute.HIGH
    },
    {
        "id": "S10",
        "name": "LOW out of scope",
        "risk": RiskLevel.LOW,
        "scope": False,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.OUT_OF_SCOPE
    },
    {
        "id": "S11",
        "name": "MEDIUM out of scope",
        "risk": RiskLevel.MEDIUM,
        "scope": False,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.MEDIUM
    },
    {
        "id": "S12",
        "name": "HIGH out of scope",
        "risk": RiskLevel.HIGH,
        "scope": False,
        "clinical": False,
        "injection": False,
        "expected": ResponseRoute.HIGH
    },
    {
        "id": "S13",
        "name": "Clinical and injection",
        "risk": RiskLevel.LOW,
        "scope": True,
        "clinical": True,
        "injection": True,
        "expected": ResponseRoute.CLINICAL
    },
    {
        "id": "S14",
        "name": "All flags with HIGH",
        "risk": RiskLevel.HIGH,
        "scope": False,
        "clinical": True,
        "injection": True,
        "expected": ResponseRoute.HIGH
    },
    {
        "id": "S15",
        "name": "All flags with MEDIUM",
        "risk": RiskLevel.MEDIUM,
        "scope": False,
        "clinical": True,
        "injection": True,
        "expected": ResponseRoute.CLINICAL
    },
    {
        "id": "S16",
        "name": "Out of scope and injection",
        "risk": RiskLevel.LOW,
        "scope": False,
        "clinical": False,
        "injection": True,
        "expected": ResponseRoute.INJECTION
    }
]


def run_evaluation():
    results = []

    print("\nSTAGE 8B - SAFEGUARDING CONTROLLER EVALUATION")
    print("=" * 65)

    for case in TEST_CASES:
        classification = MessageClassification(
            wellbeing_scope=case["scope"],
            safeguarding_risk=case["risk"],
            clinical_request=case["clinical"],
            prompt_injection=case["injection"],
            risk_reason="Synthetic safeguarding evaluation case."
        )

        decision = control_response(classification)

        route_correct = decision.route == case["expected"]

        # Current controller returns False for all routes.
        # These flags indicate which routes are permitted
        # to reach LLM Call 2 in chat.py.
        allowed_generation = decision.route in (
            ResponseRoute.LOW,
            ResponseRoute.MEDIUM
        )

        blocked_generation = not allowed_generation

        expected_blocked = case["expected"] not in (
            ResponseRoute.LOW,
            ResponseRoute.MEDIUM
        )

        passed = (
            route_correct
            and blocked_generation == expected_blocked
        )

        results.append({
            "id": case["id"],
            "name": case["name"],
            "expected_route": case["expected"].value,
            "actual_route": decision.route.value,
            "route_correct": route_correct,
            "generation_blocked": blocked_generation,
            "expected_generation_blocked": expected_blocked,
            "passed": passed
        })

        print(
            f'{case["id"]}: '
            f'{"PASS" if passed else "FAIL"} | '
            f'Expected: {case["expected"].value} | '
            f'Actual: {decision.route.value} | '
            f'Generation blocked: {blocked_generation}'
        )

    total = len(results)
    passed_count = sum(row["passed"] for row in results)

    accuracy = (passed_count / total) * 100 if total else 0

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
    print(f"Total cases: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total - passed_count}")
    print(f"Controller rule accuracy: {accuracy:.1f}%")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()
