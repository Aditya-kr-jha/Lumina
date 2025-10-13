from datetime import datetime, timezone, date
from enum import Enum
from typing import Any, Dict, List, Optional, Annotated

from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict


class DocumentStatus(str, Enum):
    """Enumeration of document processing states."""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class UserStatus(str, Enum):
    """User account status values."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base fields for user data."""

    username: str = Field(..., min_length=3, max_length=50)
    email: Annotated[str, EmailStr] = Field(...)
    status: UserStatus = Field(default=UserStatus.ACTIVE)


class UserRead(UserBase):
    """Schema for user data in responses."""

    id: int
    role: Optional[UserRole] = Field(default=UserRole.USER)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[Annotated[str, EmailStr]] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserCreateByAdmin(UserCreate):
    """Schema for admin creating users with specific roles."""

    role: UserRole = Field(default=UserRole.USER)


class DocumentUploadResponse(BaseModel):
    """Response model returned after a document upload."""

    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    status: DocumentStatus = Field(..., description="Current processing status")
    pages: Optional[int] = Field(None, ge=0, description="Number of pages in document")
    upload_time: datetime = Field(..., description="Timestamp of upload")
    message: str = Field(..., description="Status message")


class DocumentInfo(BaseModel):
    """Metadata for a processed document."""

    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    pages: int = Field(..., ge=0, description="Total number of pages")
    upload_time: datetime = Field(..., description="Upload timestamp")
    status: DocumentStatus = Field(..., description="Processing status")
    chunk_count: int = Field(..., ge=0, description="Number of text chunks")


class DocumentListResponse(BaseModel):
    """Response containing a list of documents."""

    documents: List[DocumentInfo] = Field(default_factory=list)
    total: int = Field(..., ge=0, description="Total number of documents")


class ChatRequest(BaseModel):
    """Request model for chat queries."""

    question: str = Field(
        ..., min_length=1, max_length=1000, description="User question"
    )
    document_id: str = Field(..., description="Target document ID")
    session_id: Optional[str] = Field(None, description="Chat session identifier")
    include_sources: bool = Field(True, description="Include source chunks in response")
    top_k: int = Field(
        4, ge=1, le=10, description="Number of source chunks to retrieve"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Validate that question is not empty after stripping whitespace."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Question cannot be empty or whitespace only")
        return stripped


class SourceChunk(BaseModel):
    """A chunk of source text with metadata."""

    content: str = Field(..., description="Text content of the chunk")
    page_number: int = Field(..., ge=1, description="Source page number")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ChatResponse(BaseModel):
    """Response model for chat queries."""

    answer: str = Field(..., description="Generated answer")
    sources: List[SourceChunk] = Field(
        default_factory=list, description="Source chunks used"
    )
    session_id: str = Field(..., description="Chat session identifier")
    document_id: str = Field(..., description="Source document ID")
    question: str = Field(..., description="Original question")
    timestamp: datetime | None = Field(None, description="Response timestamp")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")


class ChatHistoryItem(BaseModel):
    """A single interaction in chat history."""

    question: str = Field(..., description="User question")
    answer: str = Field(..., description="System answer")


class ChatHistoryResponse(BaseModel):
    """Complete chat history for a session."""

    session_id: str = Field(..., description="Chat session identifier")
    document_id: str = Field(..., description="Document ID")
    history: List[ChatHistoryItem] = Field(
        default_factory=list, description="Chat history"
    )
    total_interactions: int = Field(
        ..., ge=0, description="Total number of interactions"
    )


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: str = Field(..., description="Error type or message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="Error timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    vector_store: str = Field(..., description="Vector store status")
    llm_model: str = Field(..., description="LLM model information")
    timestamp: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="Check timestamp"
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
