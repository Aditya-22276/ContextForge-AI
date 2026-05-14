from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db

from services.dependencies import get_current_user

from models.chat_session import ChatSession


router = APIRouter()


# -----------------------------------
# GET ALL CHAT SESSIONS
# -----------------------------------
@router.get("/sessions")
def get_sessions(

    db: Session = Depends(get_db),

    user_id: int = Depends(get_current_user)

):

    print("FETCHING SESSIONS")

    sessions = (

        db.query(ChatSession)

        .filter(
            ChatSession.user_id == user_id
        )

        .order_by(
            ChatSession.created_at.desc()
        )

        .all()

    )

    return [

        {
            "id": session.id,

            "title": (
                session.title
                if session.title
                else "New Chat"
            ),

            "created_at": session.created_at
        }

        for session in sessions

    ]