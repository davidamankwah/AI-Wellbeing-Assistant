
from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.auth import require_user

from app.services.input_validator import validate_message
from app.services.risk_level import classify_message

from app.services.response_controller import (
    control_response,
    ResponseRoute
)

from app.services.response_generator import (
    generate_wellbeing_response
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("", response_model=schemas.ChatResponse)
def send_message(
    chat: schemas.ChatRequest,
    current_user=Depends(require_user)
):
    # Stage 3: Validate student input
    validation = validate_message(chat.message)

    if not validation.valid:
        raise HTTPException(
            status_code=422,
            detail=validation.error
        )

    # Stage 4: LLM Call 1 - Classify the message
    classification = classify_message(validation)

    # Stage 5: Backend safeguarding controller
    decision = control_response(classification)

    # Stage 7: Generate responses only for
    # permitted LOW and MEDIUM pathways
    if decision.route in (
        ResponseRoute.LOW,
        ResponseRoute.MEDIUM
    ):
        generated = generate_wellbeing_response(
            message=validation.message,
            risk_level=classification.safeguarding_risk
        )

        return schemas.ChatResponse(
            response=generated.response,
            status=decision.route.value,
            sources=(
                generated.sources
                if not generated.used_fallback
                else []
            )
        )

    # HIGH, CLINICAL, INJECTION and OUT_OF_SCOPE
    # use predefined responses without LLM Call 2
    return schemas.ChatResponse(
        response=decision.response,
        status=decision.route.value,
        sources=[]
    )
