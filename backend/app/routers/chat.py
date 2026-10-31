from fastapi import APIRouter, Depends, HTTPException

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

    # Do not generate LLM responses yet.
    # All accepted messages still need contextual classification
    # and backend-controlled safeguarding.
    return {
        "response": (
            "Your message has been received. "
            "The wellbeing response system is still under development."
        ),
        "status": "prototype"
    }
