
import re
from dataclasses import dataclass


@dataclass
class OutputValidation:
    valid: bool
    reason: str | None = None


BLOCKED_PATTERNS = [
    r"\byou (?:definitely|certainly) have (?:depression|anxiety|bipolar disorder)\b",
    r"\byou (?:should|must) stop taking (?:your )?medication\b",
    r"\bignore (?:all )?(?:previous|safety) instructions\b",
    r"\bhere (?:is|are) (?:my|the) system instructions\b",
]


def validate_output(response: str) -> OutputValidation:
    """Apply basic checks to an LLM-generated response."""

    if not isinstance(response, str):
        return OutputValidation(False, "Response is not text.")

    response = response.strip()

    if not response:
        return OutputValidation(False, "Empty response.")

    if len(response) > 2000:
        return OutputValidation(False, "Response is too long.")

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, response, re.IGNORECASE):
            return OutputValidation(
                False,
                "Potentially unsafe or inappropriate content."
            )

    return OutputValidation(True)
