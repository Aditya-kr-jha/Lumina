from enum import Enum

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, Relationship, select
from typing import Optional, List
from datetime import datetime, timezone

from app.models.schemas import UserStatus, UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.TIMESTAMP(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.TIMESTAMP(timezone=True),
    )

    # Relationship
    documents: List["UserDocument"] = Relationship(back_populates="user")


class UserDocument(SQLModel, table=True):
    """Links users to their documents - matches DocumentInfo schema"""

    __tablename__ = "user_documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    document_id: str = Field(index=True, max_length=32)
    filename: str = Field(max_length=255)
    file_size: int = Field(ge=0)
    pages: int = Field(ge=0)
    upload_time: datetime = Field(default_factory=datetime.now(timezone.utc))
    status: str = Field(default="uploading", max_length=20)  # Store as string in DB
    chunk_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.TIMESTAMP(timezone=True),
    )

    # Relationships
    user: "User" = Relationship(back_populates="documents")

    class Config:
        arbitrary_types_allowed = True

    def to_document_info(self) -> "DocumentInfo":
        """Convert database model to API response schema"""
        from app.models.schemas import DocumentInfo, DocumentStatus

        return DocumentInfo(
            document_id=self.document_id,
            filename=self.filename,
            file_size=self.file_size,
            pages=self.pages,
            upload_time=self.upload_time,
            status=DocumentStatus(self.status),
            chunk_count=self.chunk_count,
        )


class QueryLog(SQLModel, table=True):
    """Query log entry for tracking user queries."""

    __tablename__ = "query_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    document_id: str = Field(index=True)
    session_id: str = Field(index=True)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )


async def get_user_async(username: str, session: AsyncSession) -> Optional[User]:
    """Retrieve a user by username using async session."""
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
