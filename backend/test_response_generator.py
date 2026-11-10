
from app.schemas import RiskLevel
from app.services.response_generator import (
    generate_wellbeing_response
)


test_cases = [
    (
        "LOW - Exam stress",
        "I'm stressed about my university exams.",
        RiskLevel.LOW
    ),
    (
        "LOW - Loneliness",
        "I've been feeling lonely at university.",
        RiskLevel.LOW
    ),
    (
        "LOW - Sleep difficulties",
        "I'm having trouble sleeping.",
        RiskLevel.LOW
    ),
    (
        "MEDIUM - Significant distress",
        "I'm overwhelmed by university work and "
        "struggling to cope with stress.",
        RiskLevel.MEDIUM
    )
]


for number, (name, message, risk) in enumerate(
    test_cases, start=1
):
    print(f"\nTest {number}: {name}")

    result = generate_wellbeing_response(
        message=message,
        risk_level=risk
    )

    print("Response:", result.response)
    print("Fallback used:", result.used_fallback)
    print("Sources:")

    for source in result.sources:
        print(
            f"- {source['title']} "
            f"({source['publisher']})"
        )
        print("  URL:", source["url"])

    print("-" * 60)


# HIGH-risk messages must never enter LLM Call 2
try:
    generate_wellbeing_response(
        message="I'm thinking about hurting myself.",
        risk_level=RiskLevel.HIGH
    )
except ValueError:
    print("\nPASS: HIGH-risk generation was blocked.")
else:
    raise AssertionError(
        "HIGH-risk messages must not use LLM Call 2."
    )
