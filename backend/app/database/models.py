"""
SQLAlchemy models.
Add your domain models here — import Base and define tables.
"""
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="New chat")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(16))       # user | assistant | system
    content: Mapped[str] = mapped_column(Text)


class Document(Base):
    __tablename__ = "documents"

    source: Mapped[str] = mapped_column(String(512))
    chunk_index: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(Text)
    embedding_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
