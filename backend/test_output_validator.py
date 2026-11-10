
from app.services.output_validator import validate_output


test_cases = [
    (
        "Supportive response",
        "It may help to plan short study breaks.",
        True
    ),
    (
        "Empty response",
        "",
        False
    ),
    (
        "Unsafe diagnosis",
        "You definitely have depression.",
        False
    ),
    (
        "Medication instruction",
        "You should stop taking your medication.",
        False
    ),
    (
        "Overlong response",
        "A" * 2100,
        False
    )
]


for name, response, expected in test_cases:
    result = validate_output(response)

    assert result.valid == expected, (
        f"Unexpected result for {name}: {result}"
    )

    print(f"PASS: {name}")

print("\nAll basic output validation tests passed!")
