from fastapi import APIRouter, Depends

from app import schemas
from app.auth import require_user

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
    # Remove Surrounding Whitespace
    message = chat.message.strip()

    # Reject whitespace-only messages
    if not message: 
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail="Message should not be blank"
        )

    # Temporary response - no LLM generation yet
    return {
         "response": (
            "Your message has been received. "
            "The wellbeing response system is still under development."
        ),
        "status": "prototype"
    }