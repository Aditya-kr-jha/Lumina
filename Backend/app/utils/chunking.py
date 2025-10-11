from typing import List, Dict, Any
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
)
from langchain.docstore.document import Document
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ChunkingStrategy:
    """Factory for creating text chunking strategies"""

    @staticmethod
    def create_splitter(strategy: str = "recursive"):
        """
        Create text splitter based on strategy

        Args:
            strategy: Chunking strategy name

        Returns:
            LangChain text splitter instance
        """
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP

        if strategy == "recursive":
            return RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""],
            )

        elif strategy == "character":
            return CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separator="\n",
            )

        elif strategy == "token":
            return TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        else:
            logger.warning(f"Unknown strategy '{strategy}', using recursive")
            return RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )


def chunk_documents(
    pages_content: List[Dict[str, Any]], document_id: str, strategy: str = "recursive"
) -> List[Document]:
    """
    Chunk document pages into smaller segments

    Args:
        pages_content: List of page dictionaries with text and metadata
        document_id: Unique document identifier
        strategy: Chunking strategy to use

    Returns:
        List of LangChain Document objects
    """
    logger.info(f"Chunking document {document_id} with strategy: {strategy}")

    splitter = ChunkingStrategy.create_splitter(strategy)
    chunks = []

    for page_data in pages_content:
        page_num = page_data["page_number"]
        text = page_data["text"]

        if not text.strip():
            logger.warning(f"Page {page_num} is empty, skipping")
            continue

        # Split text into chunks
        page_chunks = splitter.split_text(text)

        # Create Document objects with metadata
        for i, chunk_text in enumerate(page_chunks):
            metadata = {
                "document_id": document_id,
                "page_number": page_num,
                "chunk_index": i,
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split()),
                "source": f"page_{page_num}_chunk_{i}",
            }

            doc = Document(page_content=chunk_text, metadata=metadata)
            chunks.append(doc)

    logger.info(f"Created {len(chunks)} chunks from {len(pages_content)} pages")
    return chunks


def get_chunk_statistics(chunks: List[Document]) -> Dict[str, Any]:
    """
    Calculate statistics about chunks

    Args:
        chunks: List of Document chunks

    Returns:
        Dictionary with chunk statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
        }

    chunk_sizes = [len(chunk.page_content) for chunk in chunks]

    return {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes),
        "total_characters": sum(chunk_sizes),
    }
