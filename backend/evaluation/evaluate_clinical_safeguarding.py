
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import MessageClassification, RiskLevel
from app.services.response_controller import (
    ResponseRoute,
    control_response
)


def make_classification(risk, clinical):
    return MessageClassification(
        wellbeing_scope=True,
        safeguarding_risk=risk,
        prompt_injection=False,
        clinical_request=clinical,
        risk_reason="Synthetic clinical safeguarding test"
    )


cases = [
    {
        "id": "CL01",
        "name": "Non-urgent diagnosis request",
        "classification": make_classification(
            RiskLevel.LOW, True
        ),
        "expected": ResponseRoute.CLINICAL,
        "required_terms": ["GP", "nhs.uk"]
    },
    {
        "id": "CL02",
        "name": "Clinical request with distress",
        "classification": make_classification(
            RiskLevel.MEDIUM, True
        ),
        "expected": ResponseRoute.CLINICAL,
        "required_terms": ["GP", "nhs.uk"]
    },
    {
        "id": "CL03",
        "name": "High-risk clinical request",
        "classification": make_classification(
            RiskLevel.HIGH, True
        ),
        "expected": ResponseRoute.HIGH,
        "required_terms": ["999", "111", "nhs.uk"]
    },
    {
        "id": "CL04",
        "name": "High risk without clinical request",
        "classification": make_classification(
            RiskLevel.HIGH, False
        ),
        "expected": ResponseRoute.HIGH,
        "required_terms": ["999", "111", "nhs.uk"]
    }
]


def main():
    print("\nCLINICAL SAFEGUARDING EVALUATION")
    print("=" * 60)

    passed = 0

    for case in cases:
        result = control_response(case["classification"])

        route_correct = result.route == case["expected"]
        generation_blocked = not result.requires_llm
        response_present = bool(result.response.strip())

        terms_present = all(
            term.lower() in result.response.lower()
            for term in case["required_terms"]
        )

        success = (
            route_correct
            and generation_blocked
            and response_present
            and terms_present
        )

        if success:
            passed += 1

        print(
            f"{case['id']}: "
            f"{'PASS' if success else 'FAIL'} | "
            f"{case['name']} | "
            f"Route: {result.route.value} | "
            f"Generation blocked: {generation_blocked}"
        )

    print("=" * 60)
    print(f"Total: {len(cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(cases) - passed}")


if __name__ == "__main__":
    main()
