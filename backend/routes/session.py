from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db

from services.dependencies import get_current_user

from models.chat_session import ChatSession
from fastapi import HTTPException
from models.chat_history import ChatHistory


router = APIRouter()


# Gets all chat sessions

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

# Delete sessions

@router.delete("/sessions/{session_id}")
def delete_session(

    session_id: int,

    db: Session = Depends(get_db),

    user_id: int = Depends(get_current_user)

):

    session = (

        db.query(ChatSession)

        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )

        .first()
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Delete chat history

    db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).delete()

    # Delete session
    db.delete(session)

    db.commit()

    return {
        "message": "Session deleted successfully"
    }