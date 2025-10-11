"""
Chat and Query API Routes
Handles document queries, conversation history, and statistics
"""

from typing import Optional
import logging
import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import settings
from app.db.session import get_async_session
from app.models.db_models import User
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatHistoryItem,
)
from app.services.chat_service import chat_service
from app.services.query_stats import query_stats_service
from app.services.vector_store import vector_store_service

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Query Routes
# ============================================================================


@router.post("/query", response_model=ChatResponse)
async def query_document(
    *,
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Ask a question about a document with conversation context (requires authentication).

    The user can only query documents they own. Maintains conversation history
    using session_id for context-aware responses.

    Args:
        request: Chat request with question, document_id, and session info
    """
    try:
        logger.info(
            f"User {current_user.id} ({current_user.username}) querying document: "
            f"{request.document_id}"
        )
        logger.info(f"Question: {request.question[:100]}...")  # Truncate long questions
        logger.debug(
            f"Query params - session_id: {request.session_id}, "
            f"include_sources: {request.include_sources}, top_k: {request.top_k}"
        )

        # Verify document exists AND user owns it
        chunks = vector_store_service.get_document_chunks(
            request.document_id, current_user.id
        )
        if not chunks:
            logger.warning(
                f"Query denied - document not found or access denied for user "
                f"{current_user.id}: {request.document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found or access denied: {request.document_id}",
            )

        logger.debug(f"Document verified with {len(chunks)} chunks")

        # Process query with user_id
        response = chat_service.query(
            question=request.question,
            document_id=request.document_id,
            user_id=current_user.id,
            session_id=request.session_id,
            include_sources=request.include_sources,
            top_k=request.top_k or settings.RETRIEVAL_TOP_K,
        )

        # Record query statistics
        await query_stats_service.record_query(
            document_id=request.document_id,
            session_id=response.session_id,
            user_id=current_user.id,
            session=session,
        )
        logger.debug("Query statistics recorded")

        logger.info(
            f"✅ Query processed successfully for user {current_user.id} - "
            f"answer length: {len(response.answer)} chars"
        )
        if request.include_sources and hasattr(response, "sources"):
            logger.debug(f"Returned {len(response.sources)} sources")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error processing query for user {current_user.id}, document {request.document_id}: "
            f"{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@router.post("/simple-query")
async def simple_query_document(
    *,
    question: str,
    document_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    top_k: int = 4,
):
    """
    Simple stateless query without conversation history (requires authentication).

    Creates a one-time session for the query. Use this for quick questions
    that don't require conversation context.

    Args:
        question: The question to ask
        document_id: Target document identifier
        top_k: Number of relevant chunks to retrieve (default: 4)
    """
    try:
        logger.info(
            f"User {current_user.id} simple query - document: {document_id}, "
            f"question: {question[:100]}..."
        )

        # Verify document exists AND user owns it
        chunks = vector_store_service.get_document_chunks(document_id, current_user.id)
        if not chunks:
            logger.warning(
                f"Simple query denied - document not found or access denied for user "
                f"{current_user.id}: {document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found or access denied: {document_id}",
            )

        logger.debug(f"Document verified with {len(chunks)} chunks")

        # Generate a simple session ID for tracking
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated session ID for simple query: {session_id}")

        # Record query statistics
        await query_stats_service.record_query(
            document_id=document_id,
            session_id=session_id,
            user_id=current_user.id,
            session=session,
        )

        # Process query with user_id
        answer = chat_service.simple_query(
            question=question,
            document_id=document_id,
            user_id=current_user.id,
            top_k=top_k,
        )

        logger.info(
            f"✅ Simple query processed for user {current_user.id} - "
            f"answer length: {len(answer)} chars"
        )

        return {
            "question": question,
            "answer": answer,
            "document_id": document_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in simple query for user {current_user.id}, document {document_id}: "
            f"{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


# ============================================================================
# Session History Routes
# ============================================================================


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    *, session_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for a session (requires authentication).

    Users can only access their own sessions. Returns all question-answer
    pairs in chronological order.

    Args:
        session_id: Session identifier
    """
    try:
        logger.info(
            f"User {current_user.id} retrieving chat history for session: {session_id}"
        )

        history = chat_service.get_session_history(session_id, current_user.id)

        if not history:
            logger.warning(
                f"Session not found or access denied for user {current_user.id}: {session_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )

        logger.debug(f"Retrieved {len(history)} history items for session {session_id}")

        # Convert to ChatHistoryItem objects
        history_items = [
            ChatHistoryItem(
                question=item["question"],
                answer=item["answer"],
            )
            for item in history
        ]

        logger.info(
            f"Returning {len(history_items)} interactions for user {current_user.id}, "
            f"session {session_id}"
        )

        return ChatHistoryResponse(
            session_id=session_id,
            document_id="",  # Would need to track per session
            history=history_items,
            total_interactions=len(history_items),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting history for user {current_user.id}, session {session_id}: "
            f"{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}",
        )


@router.get("/sessions")
async def get_active_sessions(*, current_user: User = Depends(get_current_user)):
    """
    Get list of active chat sessions for the current user.

    Returns session IDs and total count for all active conversations.
    """
    try:
        logger.info(f"User {current_user.id} requesting active sessions list")

        sessions = chat_service.get_active_sessions(current_user.id)
        session_count = chat_service.get_user_session_count(current_user.id)

        logger.info(f"User {current_user.id} has {session_count} active sessions")
        logger.debug(f"Session IDs: {sessions}")

        return {
            "user_id": current_user.id,
            "total_sessions": session_count,
            "session_ids": sessions,
        }

    except Exception as e:
        logger.error(
            f"Error getting sessions for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}",
        )


# ============================================================================
# Session Management Routes
# ============================================================================


@router.delete("/session/{session_id}")
async def clear_session(
    *, session_id: str, current_user: User = Depends(get_current_user)
):
    """
    Clear a conversation session (requires authentication).

    Users can only clear their own sessions. This deletes all conversation
    history for the specified session.

    Args:
        session_id: Session to clear
    """
    try:
        logger.warning(
            f"User {current_user.id} ({current_user.username}) clearing session: {session_id}"
        )

        success = chat_service.clear_session(session_id, current_user.id)

        if not success:
            logger.warning(
                f"Session not found or already cleared for user {current_user.id}: {session_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )

        logger.info(f"✅ Session cleared successfully: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "message": "Session cleared successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error clearing session {session_id} for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing session: {str(e)}",
        )


@router.delete("/sessions/clear-all")
async def clear_all_sessions(*, current_user: User = Depends(get_current_user)):
    """
    Clear all conversation sessions for the current user.

    This is a bulk operation that removes all session history for the user.
    Cannot be undone.
    """
    try:
        logger.warning(
            f"User {current_user.id} ({current_user.username}) clearing ALL sessions"
        )

        count = chat_service.clear_all_user_sessions(current_user.id)

        logger.info(f"✅ Cleared {count} sessions for user {current_user.id}")

        return {
            "success": True,
            "user_id": current_user.id,
            "sessions_cleared": count,
            "message": f"Cleared {count} sessions successfully",
        }

    except Exception as e:
        logger.error(
            f"Error clearing all sessions for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing sessions: {str(e)}",
        )


# ============================================================================
# Statistics Routes
# ============================================================================


@router.get("/stats/queries")
async def get_query_statistics(
    *,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get query statistics for the current user.

    Returns aggregated metrics about the user's query activity.
    """
    try:
        logger.info(f"User {current_user.id} requesting query statistics")

        stats = await query_stats_service.get_user_stats(current_user.id, session)

        logger.debug(f"Retrieved query statistics for user {current_user.id}: {stats}")

        return stats
    except Exception as e:
        logger.error(
            f"Error getting query statistics for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}",
        )


@router.get("/stats/document/{document_id}")
async def get_document_query_stats(
    *,
    document_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get query statistics for a specific document (user's own documents only).

    Returns metrics about how many queries were made against this document.

    Args:
        document_id: Document identifier
    """
    try:
        logger.info(
            f"User {current_user.id} requesting statistics for document: {document_id}"
        )

        # Verify user owns document
        chunks = vector_store_service.get_document_chunks(document_id, current_user.id)
        if not chunks:
            logger.warning(
                f"Stats access denied - document not found or access denied for user "
                f"{current_user.id}: {document_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        logger.debug(f"Document ownership verified for stats request")

        stats = await query_stats_service.get_document_stats(
            document_id, current_user.id, session
        )

        logger.debug(f"Retrieved document statistics for {document_id}: {stats}")

        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting document stats for user {current_user.id}, document {document_id}: "
            f"{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document statistics: {str(e)}",
        )


@router.get("/stats/session/{session_id}")
async def get_session_query_stats(
    *,
    session_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get query statistics for a specific session (user's own sessions only).

    Returns metrics about query activity within this conversation session.

    Args:
        session_id: Session identifier
    """
    try:
        logger.info(
            f"User {current_user.id} requesting statistics for session: {session_id}"
        )

        stats = await query_stats_service.get_session_stats(
            session_id, current_user.id, session
        )

        logger.debug(f"Retrieved session statistics for {session_id}: {stats}")

        return stats
    except Exception as e:
        logger.error(
            f"Error getting session stats for user {current_user.id}, session {session_id}: "
            f"{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session statistics: {str(e)}",
        )
