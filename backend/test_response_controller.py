
from app.schemas import MessageClassification, RiskLevel
from app.services.response_controller import control_response


test_cases = [
    (
        "LOW - Exam stress",
        MessageClassification(
            wellbeing_scope=True,
            safeguarding_risk=RiskLevel.LOW,
            prompt_injection=False,
            clinical_request=False,
            risk_reason="General academic stress."
        ),
        "LOW"
    ),
    (
        "MEDIUM - Significant distress",
        MessageClassification(
            wellbeing_scope=True,
            safeguarding_risk=RiskLevel.MEDIUM,
            prompt_injection=False,
            clinical_request=False,
            risk_reason="Significant emotional distress."
        ),
        "MEDIUM"
    ),
    (
        "HIGH - Self-harm concern",
        MessageClassification(
            wellbeing_scope=True,
            safeguarding_risk=RiskLevel.HIGH,
            prompt_injection=False,
            clinical_request=False,
            risk_reason="Possible self-harm intent."
        ),
        "HIGH"
    ),
    (
        "Clinical - Diagnosis request",
        MessageClassification(
            wellbeing_scope=True,
            safeguarding_risk=RiskLevel.LOW,
            prompt_injection=False,
            clinical_request=True,
            risk_reason="Request for diagnosis."
        ),
        "CLINICAL"
    ),
    (
        "Injection - Reveal instructions",
        MessageClassification(
            wellbeing_scope=False,
            safeguarding_risk=RiskLevel.LOW,
            prompt_injection=True,
            clinical_request=False,
            risk_reason="Prompt injection attempt."
        ),
        "INJECTION"
    ),
    (
        "Out of scope - Order pizza",
        MessageClassification(
            wellbeing_scope=False,
            safeguarding_risk=RiskLevel.LOW,
            prompt_injection=False,
            clinical_request=False,
            risk_reason="Unrelated food request."
        ),
        "OUT_OF_SCOPE"
    ),
    (
        "HIGH + Injection - Priority test",
        MessageClassification(
            wellbeing_scope=False,
            safeguarding_risk=RiskLevel.HIGH,
            prompt_injection=True,
            clinical_request=False,
            risk_reason="Safety concern with injection."
        ),
        "HIGH"
    ),
    (
        "MEDIUM + Clinical - Priority test",
        MessageClassification(
            wellbeing_scope=True,
            safeguarding_risk=RiskLevel.MEDIUM,
            prompt_injection=False,
            clinical_request=True,
            risk_reason="Distress with diagnosis request."
        ),
        "MEDIUM"
    ),
]


for number, (name, classification, expected) in enumerate(
    test_cases, start=1
):
    result = control_response(classification)

    passed = result.route.value == expected

    print(f"\nTest {number}: {name}")
    print("Expected:", expected)
    print("Actual:", result.route.value)
    print("Requires LLM:", result.requires_llm)
    print("Result:", "PASS" if passed else "FAIL")
    print("-" * 50)

    assert passed, f"Incorrect routing for {name}"

print("\nAll response controller tests passed!")
