from fastapi import APIRouter, Depends, HTTPException
from app.services.risk_level import classify_message
from app.services.response_controller import control_response
from app import schemas
from app.auth import require_user
from app.services.input_validator import validate_message

#Create a router for chat-based endpoints
router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("", response_model=schemas.ChatResponse)
def send_message(
    chat: schemas.ChatRequest,
    current_user=Depends(require_user)
):
    # Stage 3: validate the submitted message
    validation = validate_message(chat.message)

    if not validation.valid:
        raise HTTPException(
            status_code=422,
            detail=validation.error
        )

   # Stage 4: LLM Call 1 - Contextual classification
    classification = classify_message(validation)

    # Stage 5: Backend-controlled safeguarding and routing
    decision = control_response(classification)

    # Return only the controlled response to the student
    return {
        "response": decision.response,
        "status": decision.route.value
    }
