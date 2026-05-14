from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey
)

from sqlalchemy.sql import func

from db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # DOCUMENT CONTENT
    content = Column(
        Text,
        nullable=False
    )

    # VECTOR EMBEDDING
    embedding = Column(
        Text,
        nullable=True
    )

    # ✅ NEW: FILENAME
    filename = Column(
        Text,
        nullable=True
    )

    # USER RELATION
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # CREATED TIME
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )