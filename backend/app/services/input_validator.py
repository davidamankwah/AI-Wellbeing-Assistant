import re
from dataclasses import dataclass, asdict

# These are screening indicators but not full risk classifiers.
# The contextual assessment will be employed in Stage 4.
MAX_MESSAGE_LENGTH = 2000

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

# Identify some typical prompt injection attacks.
INJECTION_PATTERNS = [
    r"\bignore (all )?(previous|prior) instructions\b",
    r"\breveal (your )?(system|developer) prompt\b",
    r"\bdisable (the )?(safety|safeguards|filters)\b",
    r"\bact as (if you are|an?) unrestricted\b",
]

@dataclass
class ValidationResult:
    valid: bool
    message: str
    error: str | None
    safety_flag: bool
    injection_flag: bool
    privacy_flag: bool

def validate_message(message: str) -> ValidationResult:
    """
    Perform preliminary input checks.

    This function does not classify LOW/MEDIUM/HIGH risk.
    It only identifies technical problems and possible
    concerns for later safeguarding assessment.
    """

    if not isinstance(message,str):
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
            False, "", "Message contains more than 2000 characters.",
            False, False, False
        )
    
    # Reject control characters except normal line breaks and tabs.
    if any(
        ord(char) < 32 and char not in "\n\r\t"
        for char in cleaned
     ):
        return ValidationResult (
            False,"","Message contains unsupported characters.",
            False, False, False
        )

    # Detect possible safety concerns.
    safety_flag = any(
        re.search(pattern,cleaned,re.IGNORECASE)
        for pattern in SAFETY_PATTERN
    )

    # Detect potential attempts to override chatbot rules.
    injection_flag = any(
        re.search(pattern, cleaned, re.IGNORECASE)
        for pattern in INJECTION_PATTERNS
    )

    # Basic email and phone-number screening.
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    phone_pattern = r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)"

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
        privacy_flag=privacy_flag
    )

def validation_to_dict(result: ValidationResult):
    return asdict(result)
        
    
    

