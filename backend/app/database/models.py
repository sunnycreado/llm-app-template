"""
SQLAlchemy models.
Add your domain models here — import Base and define tables.
"""
from sqlalchemy import Boolean, Float, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
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


class PromptVersion(Base):
    """
    DB-backed prompt versioning.

    One row per version per prompt name.
    is_active=True marks the live version for that name.
    Only one version per name can be active at a time.

    Promote a version:
        UPDATE prompt_versions SET is_active=false WHERE name='base';
        UPDATE prompt_versions SET is_active=true  WHERE name='base' AND version='v2';

    Or use the API: POST /api/prompts/{name}/{version}/promote
    """
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_name_version"),
        Index("ix_prompt_active", "name", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    system: Mapped[str] = mapped_column(Text, nullable=False)
    few_shot: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    eval_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
