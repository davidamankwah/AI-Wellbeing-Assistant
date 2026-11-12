
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.input_validator import validate_message

CASES = [
    (
        "I want to hurt myself.",
        True
    ),
    (
        "I'm thinking about hurting myself.",
        True
    ),
    (
        "I want to end my life.",
        True
    ),
    (
        "We discussed suicide prevention in class today.",
        False
    ),
    (
        "I'm researching self-harm prevention.",
        False
    ),
    (
        "We discussed suicide in class, and now I want to hurt myself.",
        True
    ),
    (
    "I'm thinking about harming myself.",
    True
    ),
    (
    "We discussed suicide prevention in class, "
    "but now I'm thinking about hurting myself.",
    True
    ),
]

passed = 0

print("\nSTAGE 9A.2 - CONTEXTUAL SAFETY SCREENING")
print("=" * 60)

for index, (message, expected) in enumerate(CASES, start=1):
    result = validate_message(message)

    actual = result.direct_risk_flag
    success = result.valid and actual == expected

    if success:
        passed += 1

    print(
        f"T{index:02}: "
        f"{'PASS' if success else 'FAIL'} | "
        f"Expected direct risk: {expected} | "
        f"Actual: {actual}"
    )

print("=" * 60)
print(f"Passed: {passed}/{len(CASES)}")
