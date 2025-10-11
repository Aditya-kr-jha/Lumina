"""
Document Management API Routes
Handles PDF upload, listing, and deletion with user authentication
Documents are processed in-memory and only metadata is persisted to database
"""

from datetime import datetime, timezone
from typing import List
import logging
import io

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth import get_current_user
from app.config import settings

from app.models.db_models import User, UserDocument
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentInfo,
    DocumentStatus,
)
from app.services.pdf_processor import pdf_processor
from app.services.vector_store import vector_store_service
from app.utils.chunking import chunk_documents, get_chunk_statistics
from app.db.session import get_async_session, AsyncSessionLocal

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Background Processing
# ============================================================================


async def process_document_background(
    *,
    file_content: bytes,
    document_id: str,
    user_id: int,
    filename: str,
):
    """
    Background processing function for PDF documents.

    Processes PDF from memory, creates embeddings, and updates database status.
    File is not persisted to disk.
    """
    # Create a new session for background task
    async with AsyncSessionLocal() as session:
        try:
            logger.info(
                f"🔄 Starting background processing for user {user_id}: {document_id}"
            )

            # Validate PDF structure from bytes
            is_valid, error_msg = pdf_processor.validate_pdf_bytes(file_content)
            if not is_valid:
                logger.error(f"Invalid PDF for user {user_id}: {error_msg}")
                await _update_document_status(session, user_id, document_id, "error")
                return

            # Extract text content from bytes
            logger.debug(f"Extracting text from {filename}")
            pages_content = pdf_processor.extract_text_from_bytes(file_content)

            # Chunk document
            logger.debug(
                f"Chunking document {document_id} with strategy: {settings.CHUNKING_STRATEGY}"
            )
            chunks = chunk_documents(
                pages_content=pages_content,
                document_id=document_id,
                strategy=settings.CHUNKING_STRATEGY,
            )

            chunk_stats = get_chunk_statistics(chunks)
            logger.info(
                f"Generated {chunk_stats['total_chunks']} chunks for {document_id}: {chunk_stats}"
            )

            # Store embeddings with user_id
            logger.debug(
                f"Adding {len(chunks)} chunks to vector store for user {user_id}"
            )
            result = vector_store_service.add_documents(
                documents=chunks, document_id=document_id, user_id=user_id
            )

            if result["success"]:
                # Update database record with success status
                await _update_document_status(
                    session,
                    user_id,
                    document_id,
                    "ready",
                    chunk_count=chunk_stats["total_chunks"],
                )

                logger.info(
                    f"✅ Background processing complete for user {user_id}: "
                    f"{document_id} ({chunk_stats['total_chunks']} chunks)"
                )
            else:
                # Update status to error
                await _update_document_status(session, user_id, document_id, "error")

                logger.error(
                    f"Failed to add document to vector store for user {user_id}: "
                    f"{result.get('error')}"
                )

        except Exception as e:
            logger.error(
                f"❌ Background processing failed for user {user_id}, document {document_id}: {e}",
                exc_info=True,
            )

            # Update status to error
            try:
                await _update_document_status(session, user_id, document_id, "error")
            except Exception as db_error:
                logger.error(f"Failed to update error status: {db_error}")


# ============================================================================
# Helper Functions
# ============================================================================


async def _update_document_status(
    session: AsyncSession,
    user_id: int,
    document_id: str,
    status: str,
    chunk_count: int | None = None,
) -> None:
    """
    Helper function to update document status in database.

    Args:
        session: Database session
        user_id: User ID
        document_id: Document ID
        status: New status ('processing', 'ready', 'error')
        chunk_count: Optional chunk count to update
    """
    try:
        stmt = select(UserDocument).where(
            UserDocument.user_id == user_id, UserDocument.document_id == document_id
        )
        result = await session.execute(stmt)
        user_doc = result.scalar_one_or_none()

        if user_doc:
            user_doc.status = status
            if chunk_count is not None:
                user_doc.chunk_count = chunk_count
            await session.commit()
            logger.debug(f"Updated document {document_id} status to: {status}")
        else:
            logger.warning(f"Document not found in DB: {document_id}")

    except Exception as e:
        logger.error(f"Error updating document status: {e}")
        await session.rollback()
        raise


# ============================================================================
# Document Upload & Processing
# ============================================================================


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    *,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Upload and process a PDF document (requires authentication).

    - Validates file type and size limits
    - Checks for duplicate documents
    - Stores metadata in database
    - Returns immediately with processing status
    - Actual processing happens in background
    - File is NOT persisted to disk
    """
    try:
        logger.info(
            f"User {current_user.id} ({current_user.username}) uploading document: "
            f"{file.filename}"
        )

        # Validate file extension
        if not file.filename.endswith(".pdf"):
            logger.warning(
                f"User {current_user.id} attempted non-PDF upload: {file.filename}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )

        # Read file content into memory
        file_content = await file.read()
        file_size = len(file_content)
        await file.close()

        # Check file size
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            logger.warning(
                f"User {current_user.id} attempted oversized upload: "
                f"{file_size / (1024*1024):.2f}MB (max: {settings.MAX_FILE_SIZE_MB}MB)"
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB",
            )

        logger.debug(f"File size validated: {file_size / (1024*1024):.2f}MB")

        # Generate document ID from content
        document_id = pdf_processor.generate_document_id_from_bytes(
            file_content, current_user.id
        )

        logger.debug(f"Generated document ID: {document_id}")

        # Check if document already exists in database
        stmt = select(UserDocument).where(
            UserDocument.user_id == current_user.id,
            UserDocument.document_id == document_id
        )
        result = await session.execute(stmt)
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            logger.info(
                f"Duplicate upload detected for user {current_user.id}: "
                f"{document_id} (existing record found)"
            )

            # Check vector store for chunks
            existing_chunks = vector_store_service.get_document_chunks(
                document_id, current_user.id
            )

            return DocumentUploadResponse(
                document_id=document_id,
                filename=existing_doc.filename,
                file_size=existing_doc.file_size,
                status=DocumentStatus(existing_doc.status),
                pages=existing_doc.pages,
                upload_time=existing_doc.upload_time,
                message=f"Document already exists with {len(existing_chunks)} chunks. Reusing existing embeddings.",
            )

        # Extract quick metadata for immediate response
        metadata = pdf_processor.extract_metadata_from_bytes(file_content)
        logger.debug(f"Extracted metadata: {metadata['pages']} pages")

        # Create database record
        user_document = UserDocument(
            user_id=current_user.id,
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            pages=metadata["pages"],
            upload_time=datetime.now(timezone.utc),
            status="processing",
            chunk_count=0,
        )

        session.add(user_document)
        await session.commit()
        await session.refresh(user_document)
        logger.debug(f"Created UserDocument record with id: {user_document.id}")

        # Queue background processing with file content
        background_tasks.add_task(
            process_document_background,
            file_content=file_content,
            document_id=document_id,
            user_id=current_user.id,
            filename=file.filename,
        )

        logger.info(
            f"📤 Document queued for processing: {document_id} "
            f"(user {current_user.id}, {metadata['pages']} pages)"
        )

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            status=DocumentStatus.PROCESSING,
            pages=metadata["pages"],
            upload_time=datetime.now(timezone.utc),
            message=f"Document uploaded successfully. Processing {metadata['pages']} pages in background.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error uploading document for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.post("/batch-upload")
async def batch_upload_documents(
    *,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Upload multiple PDF documents at once (requires authentication).

    Processes each file independently. Partial success is possible.
    """
    logger.info(f"User {current_user.id} batch uploading {len(files)} documents")

    results = []
    errors = []

    for idx, file in enumerate(files, 1):
        try:
            logger.debug(f"Processing batch file {idx}/{len(files)}: {file.filename}")
            result = await upload_document(
                background_tasks=background_tasks,
                file=file,
                current_user=current_user,
                session=session,
            )
            results.append(result)
        except HTTPException as e:
            logger.warning(f"Batch upload failed for {file.filename}: {e.detail}")
            errors.append({"filename": file.filename, "error": e.detail})
        except Exception as e:
            logger.error(f"Unexpected error in batch upload for {file.filename}: {e}")
            errors.append({"filename": file.filename, "error": str(e)})

    logger.info(
        f"Batch upload complete for user {current_user.id}: "
        f"{len(results)} succeeded, {len(errors)} failed"
    )

    return {
        "user_id": current_user.id,
        "success": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }


# ============================================================================
# Document Query & Status
# ============================================================================


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    *,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all uploaded documents for the current user.

    Returns metadata for all documents owned by the authenticated user from database.
    """
    try:
        logger.info(f"User {current_user.id} listing documents")

        # Query database for user's documents
        stmt = select(UserDocument).where(UserDocument.user_id == current_user.id)
        result = await session.execute(stmt)
        user_documents = result.scalars().all()

        logger.debug(f"Found {len(user_documents)} documents in database")

        # Convert to DocumentInfo schema
        documents = [doc.to_document_info() for doc in user_documents]

        logger.info(f"Returning {len(documents)} documents for user {current_user.id}")

        return DocumentListResponse(documents=documents, total=len(documents))

    except Exception as e:
        logger.error(
            f"Error listing documents for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}",
        )


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    *,
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get information about a specific document (requires ownership).

    Returns detailed metadata for the requested document from database.
    """
    try:
        logger.info(f"User {current_user.id} getting document info: {document_id}")

        # Query database for document
        stmt = select(UserDocument).where(
            UserDocument.user_id == current_user.id,
            UserDocument.document_id == document_id
        )
        result = await session.execute(stmt)
        user_doc = result.scalar_one_or_none()

        if not user_doc:
            logger.warning(
                f"Document not found or access denied for user {current_user.id}: {document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Retrieved metadata for {document_id} from database")

        return user_doc.to_document_info()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting document {document_id} for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}",
        )


@router.get("/{document_id}/status")
async def get_document_status(
    *,
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Check if a document has finished processing.

    Returns processing status and chunk count if ready.
    """
    try:
        logger.debug(
            f"User {current_user.id} checking status for document: {document_id}"
        )

        # Query database for document
        stmt = select(UserDocument).where(
            UserDocument.user_id == current_user.id,
            UserDocument.document_id == document_id
        )
        result = await session.execute(stmt)
        user_doc = result.scalar_one_or_none()

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Document {document_id} status: {user_doc.status}")

        return {
            "document_id": document_id,
            "status": DocumentStatus(user_doc.status),
            "chunk_count": user_doc.chunk_count,
            "message": f"Document is {user_doc.status}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error checking status for document {document_id}, user {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking status: {str(e)}",
        )


# ============================================================================
# Document Deletion
# ============================================================================


@router.delete("/{document_id}")
async def delete_document(
    *,
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Delete a document and its embeddings (requires ownership).

    Removes both the database record and all associated vector embeddings.
    """
    try:
        logger.warning(
            f"User {current_user.id} ({current_user.username}) deleting document: {document_id}"
        )

        # Query database for document
        stmt = select(UserDocument).where(
            UserDocument.user_id == current_user.id,
            UserDocument.document_id == document_id
        )
        result = await session.execute(stmt)
        user_doc = result.scalar_one_or_none()

        if not user_doc:
            logger.warning(
                f"Delete failed - document not found or access denied for user {current_user.id}: "
                f"{document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Verified ownership for document {document_id}")

        # Delete from vector store
        logger.debug(
            f"Deleting embeddings from vector store for document: {document_id}"
        )
        vector_result = vector_store_service.delete_document(document_id, current_user.id)

        chunks_deleted = vector_result.get('chunks_deleted', 0) if vector_result["success"] else 0

        if not vector_result["success"]:
            logger.warning(
                f"Failed to delete from vector store for user {current_user.id}: "
                f"{vector_result.get('error')}"
            )

        # Delete from database
        await session.delete(user_doc)
        await session.commit()

        logger.info(
            f"✅ Document deleted by user {current_user.id}: {document_id} "
            f"({chunks_deleted} chunks removed)"
        )

        return {
            "success": True,
            "document_id": document_id,
            "message": "Document deleted successfully",
            "chunks_deleted": chunks_deleted,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting document {document_id} for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


# ============================================================================
# User Statistics
# ============================================================================


@router.get("/stats/user")
async def get_user_document_stats(
    *,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get statistics about the current user's documents.

    Returns document count, total chunks, and document IDs from database.
    """
    try:
        logger.info(f"User {current_user.id} requesting document statistics")

        # Query database for user's documents
        stmt = select(UserDocument).where(UserDocument.user_id == current_user.id)
        result = await session.execute(stmt)
        user_documents = result.scalars().all()

        document_ids = [doc.document_id for doc in user_documents]
        total_chunks = sum(doc.chunk_count for doc in user_documents)

        logger.info(
            f"User {current_user.id} stats: {len(document_ids)} documents, "
            f"{total_chunks} total chunks"
        )

        return {
            "user_id": current_user.id,
            "total_documents": len(document_ids),
            "total_chunks": total_chunks,
            "document_ids": document_ids,
        }
    except Exception as e:
        logger.error(
            f"Error getting stats for user {current_user.id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}",
        )
