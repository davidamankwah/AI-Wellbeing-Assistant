
import re
from dataclasses import dataclass, asdict

MAX_MESSAGE_LENGTH = 2000

# Broad indicators that require safeguarding attention.
SAFETY_PATTERN = [
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bhurt(?:ing)? myself\b",
    r"\bharm(?:ing)? myself\b",
    r"\bsuicid(?:e|al)\b",
    r"\bself[- ]harm(?:ing)?\b",
    r"\boverdos(?:e|ing)\b",
    r"\bhurt(?:ing)? someone\b",
    r"\bkill(?:ing)? someone\b",
    r"\btake my own life\b",
    r"\bdon't want to (?:live|be alive) anymore\b",
]

# Explicit personal-risk indicators.
# These trigger conservative HIGH handling.
#
# This list is not exhaustive and does not constitute
# a validated clinical risk-detection system.
DIRECT_RISK_PATTERNS = [
    
    r"\b(?:i(?:'m| am) thinking about|i want to|i plan to|i might)\s+(?:hurt(?:ing)?|harm(?:ing)?|kill(?:ing)?)\s+myself\b",
    r"\b(?:i want to|i plan to|i might)\s+(?:end my life|take my own life)\b",
    r"\b(?:i(?:'m| am) thinking about|i want to|i plan to)\s+(?:suicide|self[- ]harm)\b",
    r"\b(?:i(?:'ve| have))\s+(?:hurt|harmed)\s+myself\b",
    r"\b(?:i(?:'ve| have))\s+(?:attempted suicide|overdosed)\b",
    r"\b(?:i(?:'m| am))\s+(?:going to|about to)\s+(?:hurt|harm|kill)\s+(?:myself|someone)\b",
    r"\b(?:i want to|i plan to|i might)\s+(?:hurt|harm|kill)\s+someone\b",
    r"\bi don['’]t want to (?:live|be alive) anymore\b",
]

INJECTION_PATTERNS = [
    r"\bignore (all )?(previous|prior) instructions\b",
    r"\breveal (your )?(system|developer) prompt\b",
    r"\bdisable (the )?(safety|safeguards|filters)\b",
    r"\bact as (if you are|an?) unrestricted\b",
    r"\bpretend you have no restrictions\b",
]

@dataclass
class ValidationResult:
    valid: bool
    message: str
    error: str | None
    safety_flag: bool
    injection_flag: bool
    privacy_flag: bool
    direct_risk_flag: bool = False


def validate_message(message: str) -> ValidationResult:
    """
    Perform technical validation and preliminary screening.

    safety_flag:
        Broad safety-related language.

    direct_risk_flag:
        Explicit personal-risk language requiring
        conservative HIGH handling.

    Neither flag is a clinical diagnosis.
    """

    if not isinstance(message, str):
        return ValidationResult(
            False, "", "Message must be text.",
            False, False, False
        )

    cleaned = message.strip()

    if not cleaned:
        return ValidationResult(
            False, "", "The message cannot be empty.",
            False, False, False
        )

    if len(cleaned) > MAX_MESSAGE_LENGTH:
        return ValidationResult(
            False, "",
            "Message contains more than 2000 characters.",
            False, False, False
        )

    if any(
        ord(char) < 32 and char not in "\n\r\t"
        for char in cleaned
    ):
        return ValidationResult(
            False, "",
            "Message contains unsupported characters.",
            False, False, False
        )

    safety_flag = any(
        re.search(pattern, cleaned, re.IGNORECASE)
        for pattern in SAFETY_PATTERN
    )

    direct_risk_flag = any(
        re.search(pattern, cleaned, re.IGNORECASE)
        for pattern in DIRECT_RISK_PATTERNS
    )

    # Direct-risk statements must also be safety flagged.
    safety_flag = safety_flag or direct_risk_flag

    injection_flag = any(
        re.search(pattern, cleaned, re.IGNORECASE)
        for pattern in INJECTION_PATTERNS
    )

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    phone_pattern = (
        r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)"
    )

    privacy_flag = bool(
        re.search(email_pattern, cleaned)
        or re.search(phone_pattern, cleaned)
    )

    return ValidationResult(
        valid=True,
        message=cleaned,
        error=None,
        safety_flag=safety_flag,
        injection_flag=injection_flag,
        privacy_flag=privacy_flag,
        direct_risk_flag=direct_risk_flag
    )


def validation_to_dict(result: ValidationResult):
    return asdict(result)