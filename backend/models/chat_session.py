from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func

from db.database import Base


class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    title = Column(
        Text,
        default="New Chat"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )