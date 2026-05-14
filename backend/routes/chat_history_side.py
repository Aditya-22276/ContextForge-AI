from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db

from models.chat_history import ChatHistory

from services.dependencies import get_current_user


router = APIRouter()


# -----------------------------
# GET CHAT HISTORY
# -----------------------------
@router.get("/chat-history")
def get_chat_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )

    return chats