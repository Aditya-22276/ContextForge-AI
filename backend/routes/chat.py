from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import get_db

from services.chat_service import (
    retrieve_relevant_docs,
    build_context
)

from services.dependencies import get_current_user

from services.gemini import (
    generate_response,
    generate_chat_title
)

from models.chat_history import ChatHistory
from models.chat_session import ChatSession


router = APIRouter()


# Request model

class ChatRequest(BaseModel):

    query: str

    top_k: int = 5

    history: list = []

    session_id: int | None = None


# Chat end point

@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    print("CHAT USER ID:", user_id)

    # checks AUTH
    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    # Empty query check

    if not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    # Chat session

    session_id = request.session_id

    if session_id is None:

        new_session = ChatSession(

            user_id=user_id,

            title=generate_chat_title(
                request.query
            )
        )

        db.add(new_session)

        db.commit()

        db.refresh(new_session)

        session_id = new_session.id

   #Loads previous chat memory

    history = []

    previous_chats = (

        db.query(ChatHistory)

        .filter(
            ChatHistory.user_id == user_id
        )

        .order_by(
            ChatHistory.created_at.desc()
        )

        .limit(6)

        .all()
    )

    for old_chat in reversed(previous_chats):

        history.append({
            "role": "user",
            "content": old_chat.question
        })

        history.append({
            "role": "assistant",
            "content": old_chat.answer
        })

   # Smart search Query

    search_query = request.query

    if history:

        last_user_message = ""

        for msg in reversed(history):

            if msg["role"] == "user":

                last_user_message = msg["content"]

                break

        search_query = (
            last_user_message
            + " "
            + request.query
        )

    # Retrives documents

    top_docs = retrieve_relevant_docs(
        search_query,
        db,
        user_id,
        request.top_k
    )

    # If no documents found

    if not top_docs:

        return {
            "session_id": session_id,
            "answer": "No documents found. Please upload data first.",
            "sources": []
        }

   # Builds context

    context, sources, confidence = build_context(
        top_docs
    )

   # Memory text

    memory_text = ""

    for msg in history:

        memory_text += (
            f"{msg['role'].upper()}: "
            f"{msg['content']}\n"
        )

   # FINAL PROMPT

    final_prompt = f"""
You are ContextForge AI.

You are an intelligent conversational AI assistant.

PREVIOUS CONVERSATION:
{memory_text}

DOCUMENT CONTEXT:
{context}

CURRENT USER QUESTION:
{request.query}

RULES:
- Answer naturally
- Use previous conversation memory
- Prefer provided context first
- Use conversation memory for follow-up questions
- If context is missing, answer using general knowledge
- Avoid hallucinations
"""

   #General answers

    answer = generate_response(
        final_prompt
    )

   #Saves chat

    chat_entry = ChatHistory(

        user_id=user_id,

        session_id=session_id,

        title=generate_chat_title(
            request.query
        ),

        question=request.query,

        answer=answer,

        sources=sources

    )

    db.add(chat_entry)

    db.commit()

    # Returns response

    return {

        "session_id": session_id,

        "answer": answer,

        "sources": sources

    }


# Gets chat history

@router.get("/history")
def get_chat_history(

    db: Session = Depends(get_db),

    user_id: int = Depends(get_current_user)

):

    print("HISTORY USER ID:", user_id)

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    chats = (

        db.query(ChatHistory)

        .filter(
            ChatHistory.user_id == user_id
        )

        .order_by(
            ChatHistory.created_at.desc()
        )

        .all()

    )

    return [

        {

            "id": chat.id,

            "session_id": chat.session_id,

            "title": chat.title,

            "question": chat.question,

            "answer": chat.answer,

            "sources": chat.sources or [],

            "created_at": chat.created_at

        }

        for chat in chats

    ]


# Gets session chat history

@router.get("/history/{session_id}")
def get_session_chat_history(

    session_id: int,

    db: Session = Depends(get_db),

    user_id: int = Depends(get_current_user)

):

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    chats = (

        db.query(ChatHistory)

        .filter(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id == session_id
        )

        .order_by(
            ChatHistory.created_at.asc()
        )

        .all()

    )

    return [

        {

            "id": chat.id,

            "title": chat.title,

            "question": chat.question,

            "answer": chat.answer,

            "sources": chat.sources or [],

            "created_at": chat.created_at

        }

        for chat in chats

    ]