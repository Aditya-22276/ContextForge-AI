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

   #primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    #User ID
    user_id = Column(
        Integer,
        nullable=False
    )

    # SESSION ID links chat to id
    session_id = Column(
        Integer,
        nullable=True
    )

    #Chat Title
    title = Column(
        Text,
        nullable=True
    )

   #user questions
    question = Column(
        Text,
        nullable=False
    )

   #AI answers
    answer = Column(
        Text,
        nullable=False
    )

   #sources and citations
    sources = Column(
        JSON,
        nullable=True
    )

   # at what time created
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )