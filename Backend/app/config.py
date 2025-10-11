import os
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

_CONFIG_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.

    All settings can be overridden via environment variables or a .env file
    located in the same directory as this config file.
    """

    # OpenAI Configuration
    LLM_MODEL: str = Field(
        default="gpt-5-nano",
        description="OpenAI LLM model name",
    )
    LLM_TEMPERATURE: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses (0.0 = deterministic, 2.0 = creative)",
    )
    LLM_MAX_TOKENS: int = Field(
        default=5000,
        ge=1,
        description="Maximum tokens in LLM response",
    )
    OPENAI_API_KEY: str = Field(
        default="fgfgrgthgfvht45564rt5ref4",
        description="OpenAI API key for LLM operations",
    )

    # Chunking Configuration
    CHUNK_SIZE: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Size of text chunks for processing",
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        ge=0,
        description="Overlap between consecutive chunks",
    )
    CHUNKING_STRATEGY: str = Field(
        default="recursive",
        description="Text chunking strategy (recursive, character, etc.)",
    )

    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model name",
    )
    EMBEDDING_DIMENSION: int = Field(
        default=1536,
        ge=1,
        description="Dimension of embedding vectors",
    )

    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = Field(
        default="chroma",
        description="Type of vector store to use",
    )
    CHROMA_PERSIST_DIRECTORY: Path = Field(
        default=Path("./data/vectorstore"),
        description="Directory for ChromaDB persistence",
    )
    COLLECTION_NAME: str = Field(
        default="pdf_documents",
        description="Name of the vector store collection",
    )

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = Field(
        default=50,
        ge=1,
        description="Maximum file size allowed in megabytes",
    )
    UPLOAD_FOLDER: Path = Field(
        default=Path("./data/uploads"),
        description="Directory for uploaded files",
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf"],
        description="List of allowed file extensions",
    )

    # RAG Configuration
    RETRIEVAL_TOP_K: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Number of top chunks to retrieve for context",
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for chunk retrieval",
    )

    # Session Management
    SESSION_HISTORY_LENGTH: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of chat interactions to store per session",
    )
    DEBUG: bool = Field(default=False, description="Turn it off for production")

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300

    ECHO: bool = True
    RELOAD: bool = True
    SECRET_KEY: str = "rhrytuejifuhru4577838478f47ty748urujruty478uru4t58y"

    @field_validator("CHUNK_OVERLAP")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        """Ensure chunk overlap is less than chunk size."""
        if "CHUNK_SIZE" in info.data and v >= info.data["CHUNK_SIZE"]:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        return v

    @field_validator("CHROMA_PERSIST_DIRECTORY", "UPLOAD_FOLDER")
    @classmethod
    def create_directory(cls, v: Path) -> Path:
        """Create directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("ALLOWED_EXTENSIONS")
    @classmethod
    def validate_extensions(cls, v: List[str]) -> List[str]:
        """Ensure all extensions start with a dot."""
        return [ext if ext.startswith(".") else f".{ext}" for ext in v]

    class Config:
        env_file = os.path.join(_CONFIG_DIR, ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
