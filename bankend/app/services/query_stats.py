from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from collections import Counter
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.db_models import QueryLog

logger = logging.getLogger(__name__)


class QueryStatsService:
    """Service for tracking and analyzing query statistics with database persistence."""

    def __init__(self):
        """Initialize the query statistics service."""
        logger.info("QueryStatsService initialized with database persistence")

    async def record_query(
        self,
        document_id: str,
        session_id: str,
        user_id: int,
        session: AsyncSession,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Record a query made by a user to the database.

        Args:
            document_id: Document being queried
            session_id: Session identifier
            user_id: User making the query
            session: Database session
            timestamp: Query timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        query_log = QueryLog(
            user_id=user_id,
            document_id=document_id,
            session_id=session_id,
            timestamp=timestamp,
        )

        session.add(query_log)
        await session.commit()

        logger.debug(
            f"Recorded query for user {user_id}, document {document_id}, session {session_id}"
        )

    async def get_user_stats(self, user_id: int, session: AsyncSession) -> Dict:
        """
        Get comprehensive statistics for a specific user from database.

        Args:
            user_id: User identifier
            session: Database session

        Returns:
            Dictionary containing user query statistics
        """
        # Get all user queries
        stmt = select(QueryLog).where(QueryLog.user_id == user_id)
        result = await session.execute(stmt)
        user_queries = result.scalars().all()

        if not user_queries:
            return {
                "user_id": user_id,
                "total_queries": 0,
                "unique_documents": 0,
                "unique_sessions": 0,
                "most_queried_document": None,
                "query_count_by_document": {},
                "first_query": None,
                "last_query": None,
            }

        # Extract data
        documents = [q.document_id for q in user_queries]
        sessions_list = [q.session_id for q in user_queries]
        timestamps = [q.timestamp for q in user_queries]

        # Count queries per document
        doc_counter = Counter(documents)
        most_queried = doc_counter.most_common(1)[0] if doc_counter else (None, 0)

        return {
            "user_id": user_id,
            "total_queries": len(user_queries),
            "unique_documents": len(set(documents)),
            "unique_sessions": len(set(sessions_list)),
            "most_queried_document": (
                {
                    "document_id": most_queried[0],
                    "query_count": most_queried[1],
                }
                if most_queried[0]
                else None
            ),
            "query_count_by_document": dict(doc_counter),
            "first_query": min(timestamps).isoformat() if timestamps else None,
            "last_query": max(timestamps).isoformat() if timestamps else None,
        }

    async def get_document_stats(
        self, document_id: str, user_id: int, session: AsyncSession
    ) -> Dict:
        """
        Get statistics for a specific document and user from database.

        Args:
            document_id: Document identifier
            user_id: User identifier
            session: Database session

        Returns:
            Dictionary containing document query statistics
        """
        stmt = select(QueryLog).where(
            and_(QueryLog.user_id == user_id, QueryLog.document_id == document_id)
        )
        result = await session.execute(stmt)
        doc_queries = result.scalars().all()

        if not doc_queries:
            return {
                "document_id": document_id,
                "user_id": user_id,
                "total_queries": 0,
                "unique_sessions": 0,
                "first_query": None,
                "last_query": None,
            }

        sessions_list = [q.session_id for q in doc_queries]
        timestamps = [q.timestamp for q in doc_queries]

        return {
            "document_id": document_id,
            "user_id": user_id,
            "total_queries": len(doc_queries),
            "unique_sessions": len(set(sessions_list)),
            "first_query": min(timestamps).isoformat() if timestamps else None,
            "last_query": max(timestamps).isoformat() if timestamps else None,
        }

    async def get_session_stats(
        self, session_id: str, user_id: int, session: AsyncSession
    ) -> Dict:
        """
        Get statistics for a specific session from database.

        Args:
            session_id: Session identifier
            user_id: User identifier
            session: Database session

        Returns:
            Dictionary containing session query statistics
        """
        stmt = select(QueryLog).where(
            and_(QueryLog.user_id == user_id, QueryLog.session_id == session_id)
        )
        result = await session.execute(stmt)
        session_queries = result.scalars().all()

        if not session_queries:
            return {
                "session_id": session_id,
                "user_id": user_id,
                "total_queries": 0,
                "unique_documents": 0,
                "first_query": None,
                "last_query": None,
            }

        documents = [q.document_id for q in session_queries]
        timestamps = [q.timestamp for q in session_queries]

        return {
            "session_id": session_id,
            "user_id": user_id,
            "total_queries": len(session_queries),
            "unique_documents": len(set(documents)),
            "documents_queried": list(set(documents)),
            "first_query": min(timestamps).isoformat() if timestamps else None,
            "last_query": max(timestamps).isoformat() if timestamps else None,
        }

    async def get_total_query_count(self, session: AsyncSession) -> int:
        """
        Get total number of queries across all users from database.

        Args:
            session: Database session

        Returns:
            Total query count
        """
        stmt = select(func.count(QueryLog.id))
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_queries_since(
        self, cutoff_date: datetime, session: AsyncSession
    ) -> int:
        """
        Get count of queries made since a specific date from database.

        Args:
            cutoff_date: Date to count from
            session: Database session

        Returns:
            Number of queries since cutoff date
        """
        stmt = select(func.count(QueryLog.id)).where(QueryLog.timestamp >= cutoff_date)
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_active_users_count(
        self, cutoff_date: datetime, session: AsyncSession
    ) -> int:
        """
        Get count of users who made queries since a specific date from database.

        Args:
            cutoff_date: Date to count from
            session: Database session

        Returns:
            Number of active users
        """
        stmt = select(func.count(func.distinct(QueryLog.user_id))).where(
            QueryLog.timestamp >= cutoff_date
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_all_stats(self, session: AsyncSession) -> Dict:
        """
        Get comprehensive statistics across all users from database.

        Args:
            session: Database session

        Returns:
            Dictionary containing platform-wide statistics
        """
        # Total queries
        total_queries_stmt = select(func.count(QueryLog.id))
        total_queries_result = await session.execute(total_queries_stmt)
        total_queries = total_queries_result.scalar() or 0

        # Unique users
        unique_users_stmt = select(func.count(func.distinct(QueryLog.user_id)))
        unique_users_result = await session.execute(unique_users_stmt)
        total_users = unique_users_result.scalar() or 0

        # Unique documents
        unique_docs_stmt = select(func.count(func.distinct(QueryLog.document_id)))
        unique_docs_result = await session.execute(unique_docs_stmt)
        unique_documents = unique_docs_result.scalar() or 0

        # Unique sessions
        unique_sessions_stmt = select(func.count(func.distinct(QueryLog.session_id)))
        unique_sessions_result = await session.execute(unique_sessions_stmt)
        unique_sessions = unique_sessions_result.scalar() or 0

        return {
            "total_queries": total_queries,
            "total_users_with_queries": total_users,
            "unique_documents_queried": unique_documents,
            "unique_sessions": unique_sessions,
        }

    async def get_user_query_count(self, user_id: int, session: AsyncSession) -> int:
        """
        Get total query count for a specific user from database.

        Args:
            user_id: User identifier
            session: Database session

        Returns:
            User's total query count
        """
        stmt = select(func.count(QueryLog.id)).where(QueryLog.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def clear_user_stats(self, user_id: int, session: AsyncSession) -> bool:
        """
        Clear all statistics for a specific user from database.

        Args:
            user_id: User identifier
            session: Database session

        Returns:
            True if stats were cleared, False if user had no stats
        """
        stmt = select(QueryLog).where(QueryLog.user_id == user_id)
        result = await session.execute(stmt)
        logs = result.scalars().all()

        if not logs:
            return False

        for log in logs:
            await session.delete(log)
        await session.commit()

        logger.info(f"Cleared {len(logs)} query logs for user {user_id}")
        return True

    async def get_all_user_ids(self, session: AsyncSession) -> List[int]:
        """
        Get list of all user IDs with query history from database.

        Args:
            session: Database session

        Returns:
            List of user IDs
        """
        stmt = select(func.distinct(QueryLog.user_id))
        result = await session.execute(stmt)
        return list(result.scalars().all())


# Global singleton instance
query_stats_service = QueryStatsService()
