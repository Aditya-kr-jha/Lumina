"""
Document Management API Routes
Handles PDF upload, listing, and deletion with user authentication
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List
import logging
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
    BackgroundTasks,
)

from app.auth import get_current_user
from app.config import settings
from app.models.db_models import User
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentInfo,
    DocumentStatus,
)
from app.services.pdf_processor import pdf_processor
from app.services.vector_store import vector_store_service
from app.utils.chunking import chunk_documents, get_chunk_statistics

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Background Processing
# ============================================================================


async def process_document_background(
    *,
    file_path: Path,
    document_id: str,
    user_id: int,
    filename: str,
):
    """
    Background processing function for PDF documents.

    Handles validation, text extraction, chunking, and embedding storage.
    """
    try:
        logger.info(
            f"🔄 Starting background processing for user {user_id}: {document_id}"
        )

        # Validate PDF structure
        is_valid, error_msg = pdf_processor.validate_pdf(file_path)
        if not is_valid:
            logger.error(f"Invalid PDF for user {user_id}: {error_msg}")
            file_path.unlink()
            return

        # Extract text content
        logger.debug(f"Extracting text from {filename}")
        pages_content = pdf_processor.extract_text(file_path)

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
        logger.debug(f"Adding {len(chunks)} chunks to vector store for user {user_id}")
        result = vector_store_service.add_documents(
            documents=chunks, document_id=document_id, user_id=user_id
        )

        if result["success"]:
            logger.info(
                f"✅ Background processing complete for user {user_id}: "
                f"{document_id} ({chunk_stats['total_chunks']} chunks)"
            )
        else:
            logger.error(
                f"Failed to add document to vector store for user {user_id}: "
                f"{result.get('error')}"
            )

    except Exception as e:
        logger.error(
            f"❌ Background processing failed for user {user_id}, document {document_id}: {e}",
            exc_info=True,
        )


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
):
    """
    Upload and process a PDF document (requires authentication).

    - Validates file type and size limits
    - Checks for duplicate documents
    - Returns immediately with processing status
    - Actual processing happens in background
    """
    temp_file_path = None

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

        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

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

        # Create user-specific upload directory
        user_upload_dir = settings.UPLOAD_FOLDER / f"user_{current_user.id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Using upload directory: {user_upload_dir}")

        # Save uploaded file temporarily to generate ID
        temp_file_path = user_upload_dir / f"temp_{file.filename}"

        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.debug(f"Temporary file saved: {temp_file_path}")
        finally:
            await file.close()

        # Generate document ID from content
        document_id = pdf_processor.generate_document_id(
            temp_file_path, current_user.id
        )

        logger.debug(f"Generated document ID: {document_id}")

        # Check if document already exists for this user
        existing_chunks = vector_store_service.get_document_chunks(
            document_id, current_user.id
        )

        if existing_chunks:
            logger.info(
                f"Duplicate upload detected for user {current_user.id}: "
                f"{document_id} ({len(existing_chunks)} existing chunks)"
            )

            # Find existing file to get metadata
            existing_file = None
            for file_path in user_upload_dir.glob("*.pdf"):
                if (
                    pdf_processor.generate_document_id(file_path, current_user.id)
                    == document_id
                ):

                    existing_file = file_path
                    break

            # Remove temp file
            temp_file_path.unlink()
            logger.debug("Removed temporary duplicate file")

            if existing_file:
                metadata = pdf_processor.extract_metadata(existing_file)

                return DocumentUploadResponse(
                    document_id=document_id,
                    filename=existing_file.name,
                    file_size=existing_file.stat().st_size,
                    status=DocumentStatus.READY,
                    pages=metadata["pages"],
                    upload_time=datetime.fromtimestamp(existing_file.stat().st_mtime),
                    message=f"Document already exists with {len(existing_chunks)} chunks. Reusing existing embeddings.",
                )

        # Document is new - rename temp file to final name
        file_path = user_upload_dir / f"{document_id}_{file.filename}"
        temp_file_path.rename(file_path)
        logger.debug(f"Renamed to final file: {file_path.name}")

        # Extract quick metadata for immediate response
        metadata = pdf_processor.extract_metadata(file_path)
        logger.debug(f"Extracted metadata: {metadata['pages']} pages")

        # Queue background processing
        background_tasks.add_task(
            process_document_background,
            file_path=file_path,
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
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
            logger.debug("Cleaned up temporary file after error")
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
                background_tasks=background_tasks, file=file, current_user=current_user
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
async def list_documents(*, current_user: User = Depends(get_current_user)):
    """
    List all uploaded documents for the current user.

    Returns metadata for all documents owned by the authenticated user.
    """
    try:
        logger.info(f"User {current_user.id} listing documents")

        # Get user's document IDs from vector store
        document_ids = vector_store_service.get_user_documents(current_user.id)
        logger.debug(f"Found {len(document_ids)} document IDs in vector store")

        documents = []
        user_upload_dir = settings.UPLOAD_FOLDER / f"user_{current_user.id}"

        if user_upload_dir.exists():
            pdf_files = list(user_upload_dir.glob("*.pdf"))
            logger.debug(f"Found {len(pdf_files)} PDF files in upload directory")

            for file_path in pdf_files:
                try:
                    # Extract metadata
                    metadata = pdf_processor.extract_metadata(file_path)
                    document_id = pdf_processor.generate_document_id(
                        file_path, current_user.id
                    )

                    # Only include if in user's document list
                    if document_id not in document_ids:
                        logger.debug(f"Skipping orphaned file: {file_path.name}")
                        continue

                    # Get chunks for this document
                    chunks = vector_store_service.get_document_chunks(
                        document_id, current_user.id
                    )

                    doc_info = DocumentInfo(
                        document_id=document_id,
                        filename=file_path.name,
                        file_size=metadata["file_size"],
                        pages=metadata["pages"],
                        upload_time=datetime.fromtimestamp(file_path.stat().st_mtime),
                        status=DocumentStatus.READY if chunks else DocumentStatus.ERROR,
                        chunk_count=len(chunks),
                    )

                    documents.append(doc_info)
                    logger.debug(
                        f"Added document: {document_id} ({len(chunks)} chunks)"
                    )

                except Exception as e:
                    logger.error(
                        f"Error processing file {file_path.name} for user {current_user.id}: {str(e)}"
                    )
                    continue
        else:
            logger.debug(f"Upload directory does not exist: {user_upload_dir}")

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
    *, document_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get information about a specific document (requires ownership).

    Returns detailed metadata for the requested document.
    """
    try:
        logger.info(f"User {current_user.id} getting document info: {document_id}")

        # Verify ownership
        chunks = vector_store_service.get_document_chunks(document_id, current_user.id)
        if not chunks:
            logger.warning(
                f"Document not found or access denied for user {current_user.id}: {document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Found {len(chunks)} chunks for document {document_id}")

        # Find document file in user's directory
        user_upload_dir = settings.UPLOAD_FOLDER / f"user_{current_user.id}"

        for file_path in user_upload_dir.glob("*.pdf"):
            doc_id = pdf_processor.generate_document_id(file_path, current_user.id)

            if doc_id == document_id:
                metadata = pdf_processor.extract_metadata(file_path)
                logger.debug(f"Retrieved metadata for {document_id}")

                return DocumentInfo(
                    document_id=document_id,
                    filename=file_path.name,
                    file_size=metadata["file_size"],
                    pages=metadata["pages"],
                    upload_time=datetime.fromtimestamp(file_path.stat().st_mtime),
                    status=DocumentStatus.READY if chunks else DocumentStatus.ERROR,
                    chunk_count=len(chunks),
                )

        logger.error(
            f"Document file not found on disk for user {current_user.id}: {document_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

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
    *, document_id: str, current_user: User = Depends(get_current_user)
):
    """
    Check if a document has finished processing.

    Returns processing status and chunk count if ready.
    """
    try:
        logger.debug(
            f"User {current_user.id} checking status for document: {document_id}"
        )

        chunks = vector_store_service.get_document_chunks(document_id, current_user.id)

        if chunks:
            logger.debug(f"Document {document_id} is ready with {len(chunks)} chunks")
            return {
                "document_id": document_id,
                "status": DocumentStatus.READY,
                "chunk_count": len(chunks),
                "message": "Document processing complete",
            }
        else:
            logger.debug(f"Document {document_id} is still processing")
            return {
                "document_id": document_id,
                "status": DocumentStatus.PROCESSING,
                "message": "Document is still processing",
            }

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
    *, document_id: str, current_user: User = Depends(get_current_user)
):
    """
    Delete a document and its embeddings (requires ownership).

    Removes both the file and all associated vector embeddings.
    """
    try:
        logger.warning(
            f"User {current_user.id} ({current_user.username}) deleting document: {document_id}"
        )

        # Verify ownership first
        chunks = vector_store_service.get_document_chunks(document_id, current_user.id)
        if not chunks:
            logger.warning(
                f"Delete failed - document not found or access denied for user {current_user.id}: "
                f"{document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Verified ownership: {len(chunks)} chunks found")

        # Find and delete file in user's directory
        user_upload_dir = settings.UPLOAD_FOLDER / f"user_{current_user.id}"
        file_deleted = False

        for file_path in user_upload_dir.glob("*.pdf"):
            doc_id = pdf_processor.generate_document_id(file_path, current_user.id)

            if doc_id == document_id:
                file_path.unlink()
                file_deleted = True
                logger.info(
                    f"Deleted file for user {current_user.id}: {file_path.name}"
                )
                break

        if not file_deleted:
            logger.error(
                f"Document file not found on disk for user {current_user.id}: {document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document file not found: {document_id}",
            )

        # Delete from vector store
        logger.debug(
            f"Deleting embeddings from vector store for document: {document_id}"
        )
        result = vector_store_service.delete_document(document_id, current_user.id)

        if not result["success"]:
            logger.warning(
                f"Failed to delete from vector store for user {current_user.id}: "
                f"{result.get('error')}"
            )

        logger.info(
            f"✅ Document deleted by user {current_user.id}: {document_id} "
            f"({result.get('chunks_deleted', 0)} chunks removed)"
        )

        return {
            "success": True,
            "document_id": document_id,
            "message": "Document deleted successfully",
            "chunks_deleted": result.get("chunks_deleted", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting document {document_id} for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


# ============================================================================
# User Statistics
# ============================================================================


@router.get("/stats/user")
async def get_user_document_stats(*, current_user: User = Depends(get_current_user)):
    """
    Get statistics about the current user's documents.

    Returns document count, total chunks, and document IDs.
    """
    try:
        logger.info(f"User {current_user.id} requesting document statistics")

        document_ids = vector_store_service.get_user_documents(current_user.id)
        logger.debug(f"Found {len(document_ids)} documents for user {current_user.id}")

        total_chunks = 0
        for doc_id in document_ids:
            chunks = vector_store_service.get_document_chunks(doc_id, current_user.id)
            total_chunks += len(chunks)

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
