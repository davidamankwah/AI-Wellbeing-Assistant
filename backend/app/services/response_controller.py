from dataclasses import dataclass
from enum import Enum

from app.schemas import MessageClassification, RiskLevel


# Defines the pathways available to the backend
class ResponseRoute(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    CLINICAL = "CLINICAL"
    INJECTION = "INJECTION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    LOW = "LOW"


# Structured result returned by the controller
@dataclass
class ControllerResult:
    route: ResponseRoute
    response: str
    requires_llm: bool


# Development example only.
# Review and approve crisis wording and contact details
# with the supervisor before student-facing deployment.
HIGH_RISK_RESPONSE = (
    "I'm sorry you're experiencing something that may "
    "put your safety at risk. You deserve support. "
    "If you or someone else is in immediate danger, "
    "or you cannot keep yourself safe, call 999 or "
    "go to A&E now. "
    "If you need urgent mental health help in England "
    "but it is not an immediate emergency, call NHS 111 "
    "and select the mental health option, or request "
    "an urgent GP appointment. "
    "If possible, reach out to someone you trust. "
    "NHS guidance: "
    "https://www.nhs.uk/nhs-services/mental-health-services/"
    "where-to-get-urgent-help-for-mental-health/"
)

MEDIUM_PLACEHOLDER = (
    "Your message has been identified as potentially "
    "requiring additional support. The restricted wellbeing "
    "response pathway is still under development."
)

LOW_PLACEHOLDER = (
    "Your message has been received. The standard wellbeing "
    "response pathway is still under development."
)

CLINICAL_RESPONSE = (
    "I can provide general wellbeing information, "
    "but I cannot diagnose mental health conditions, "
    "prescribe medication or recommend treatment changes. "
    "A GP or qualified mental health professional can "
    "discuss your symptoms and help you access appropriate "
    "assessment and support. "
    "In England, eligible people can also refer themselves "
    "to NHS talking therapies. "
    "NHS guidance: "
    "https://www.nhs.uk/mental-health/social-care-and-your-rights/"
    "how-to-access-mental-health-services/"
)

INJECTION_RESPONSE = (
    "I can help with student mental wellbeing, but I cannot "
    "change or reveal my internal instructions."
)

OUT_OF_SCOPE_RESPONSE = (
    "This assistant focuses on student mental wellbeing. "
    "You can ask about stress, loneliness, emotional "
    "wellbeing, or ways to find appropriate support."
)


def control_response(
    classification: MessageClassification
) -> ControllerResult:
    """
    Select a response pathway using backend rules.

    The classifier provides information, but Python
    decides which pathway is allowed.

    Priority:
    HIGH > CLINICAL > INJECTION > MEDIUM >
    OUT_OF_SCOPE > LOW
    """

    # Priority 1: HIGH-risk safeguarding
    # Always return a predefined safety response.
    # Never send HIGH-risk messages to LLM Call 2.
    if classification.safeguarding_risk == RiskLevel.HIGH:
        return ControllerResult(
            route=ResponseRoute.HIGH,
            response=HIGH_RISK_RESPONSE,
            requires_llm=False
        )

    # Priority 2: Clinical boundary
    # Prevent diagnosis, medication, and treatment
    # requests from reaching normal LLM generation.
    if classification.clinical_request:
        return ControllerResult(
            route=ResponseRoute.CLINICAL,
            response=CLINICAL_RESPONSE,
            requires_llm=False
        )

    # Priority 3: Prompt injection
    # Reject attempts to override system instructions
    # before considering LLM-generated responses.
    if classification.prompt_injection:
        return ControllerResult(
            route=ResponseRoute.INJECTION,
            response=INJECTION_RESPONSE,
            requires_llm=False
        )

    # Priority 4: MEDIUM-risk safeguarding
    # Route significant distress to the restricted
    # response pathway.
    if classification.safeguarding_risk == RiskLevel.MEDIUM:
        return ControllerResult(
            route=ResponseRoute.MEDIUM,
            response=MEDIUM_PLACEHOLDER,
            requires_llm=False
        )

    # Priority 5: Out-of-scope messages
    # Redirect unrelated requests to wellbeing topics.
    if not classification.wellbeing_scope:
        return ControllerResult(
            route=ResponseRoute.OUT_OF_SCOPE,
            response=OUT_OF_SCOPE_RESPONSE,
            requires_llm=False
        )

    # Priority 6: LOW-risk wellbeing messages
    # Allow the standard wellbeing response pathway.
    return ControllerResult(
        route=ResponseRoute.LOW,
        response=LOW_PLACEHOLDER,
        requires_llm=False
    )
