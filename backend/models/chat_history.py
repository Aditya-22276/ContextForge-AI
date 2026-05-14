from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    JSON
)

from sqlalchemy.sql import func

from db.database import Base


class ChatHistory(Base):

    __tablename__ = "chat_history"

    # -----------------------------
    # PRIMARY KEY
    # -----------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # -----------------------------
    # USER ID
    # -----------------------------
    user_id = Column(
        Integer,
        nullable=False
    )

    # -----------------------------
    # SESSION ID
    # Links chats to a session
    # -----------------------------
    session_id = Column(
        Integer,
        nullable=True
    )

    # -----------------------------
    # CHAT TITLE
    # -----------------------------
    title = Column(
        Text,
        nullable=True
    )

    # -----------------------------
    # USER QUESTION
    # -----------------------------
    question = Column(
        Text,
        nullable=False
    )

    # -----------------------------
    # AI ANSWER
    # -----------------------------
    answer = Column(
        Text,
        nullable=False
    )

    # -----------------------------
    # SOURCES / CITATIONS
    # -----------------------------
    sources = Column(
        JSON,
        nullable=True
    )

    # -----------------------------
    # CREATED TIME
    # -----------------------------
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )