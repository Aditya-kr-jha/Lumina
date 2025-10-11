from datetime import datetime, timezone, timedelta
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth import get_current_user, hash_password, verify_password
from app.db.session import get_async_session
from app.models.db_models import User, UserDocument
from app.models.schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserPasswordChange,
    UserRole,
    UserCreateByAdmin,
)
from query_stats import query_stats_service

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Dependencies
# ============================================================================


async def get_admin_user(*, current_user: User = Depends(get_current_user)) -> User:
    """Verify current user is an admin."""
    logger.info(f"Admin access check for user: {current_user.username}")
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user {current_user.username} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# ============================================================================
# Helper Functions
# ============================================================================


async def check_username_exists(
    *, username: str, session: AsyncSession, exclude_user_id: int | None = None
) -> bool:
    """Check if username already exists."""
    logger.debug(f"Checking if username exists: {username}")
    statement = select(User).where(User.username == username)
    if exclude_user_id:
        statement = statement.where(User.id != exclude_user_id)

    result = await session.execute(statement)
    exists = result.scalar_one_or_none() is not None
    logger.debug(f"Username {username} exists: {exists}")
    return exists


async def check_email_exists(
    *, email: str, session: AsyncSession, exclude_user_id: int | None = None
) -> bool:
    """Check if email already exists."""
    logger.debug(f"Checking if email exists: {email}")
    statement = select(User).where(User.email == email)
    if exclude_user_id:
        statement = statement.where(User.id != exclude_user_id)

    result = await session.execute(statement)
    exists = result.scalar_one_or_none() is not None
    logger.debug(f"Email {email} exists: {exists}")
    return exists


# ============================================================================
# Public Routes
# ============================================================================


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Register a new user account (public endpoint).

    Creates a new user with USER role. Username and email must be unique.
    """
    logger.info(
        f"Registration attempt for username: {user_create.username}, email: {user_create.email}"
    )

    # Check if username exists
    if await check_username_exists(username=user_create.username, session=session):
        logger.warning(
            f"Registration failed: Username {user_create.username} already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    if await check_email_exists(email=user_create.email, session=session):
        logger.warning(f"Registration failed: Email {user_create.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with default role (USER)
    logger.debug(f"Creating new user: {user_create.username}")
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        role=UserRole.USER,
        status=user_create.status,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(
        f"User registered successfully: ID={new_user.id}, username={new_user.username}"
    )
    return new_user


# ============================================================================
# Current User Routes
# ============================================================================


@router.get("/me", response_model=UserRead)
async def get_current_user_info(*, current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information."""
    logger.info(f"User {current_user.username} requested their profile")
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    *,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update current user's information."""
    logger.info(f"User {current_user.username} updating profile")

    # Update email if provided
    if user_update.email is not None:
        logger.debug(f"Attempting to update email to: {user_update.email}")
        if await check_email_exists(
            email=user_update.email, session=session, exclude_user_id=current_user.id
        ):
            logger.warning(f"Email update failed: {user_update.email} already in use")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = user_update.email

    # Update timestamp
    current_user.updated_at = datetime.now(timezone.utc)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    logger.info(f"User {current_user.username} profile updated successfully")
    return current_user


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    *,
    password_change: UserPasswordChange,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Change current user's password."""
    logger.info(f"User {current_user.username} attempting password change")

    # Verify current password
    if not verify_password(
        password_change.current_password, current_user.hashed_password
    ):
        logger.warning(
            f"Password change failed: Incorrect current password for {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    current_user.hashed_password = hash_password(password_change.new_password)
    current_user.updated_at = datetime.now(timezone.utc)

    session.add(current_user)
    await session.commit()

    logger.info(f"Password changed successfully for user {current_user.username}")
    return {"message": "Password changed successfully"}


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_current_user(
    *,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Delete current user's account."""
    logger.warning(
        f"User {current_user.username} (ID={current_user.id}) deleting their account"
    )

    await session.delete(current_user)
    await session.commit()

    logger.info(f"User account deleted: {current_user.username}")
    return {"message": "User account deleted successfully"}


# ============================================================================
# Admin Routes - User Management
# ============================================================================


@router.get("/", response_model=List[UserRead])
async def list_all_users(
    *,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
):
    """List all users with pagination (admin only)."""
    logger.info(f"Admin {admin.username} listing users (skip={skip}, limit={limit})")

    statement = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await session.execute(statement)
    users = result.scalars().all()

    logger.debug(f"Retrieved {len(users)} users")
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    *,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
):
    """Get any user by ID (admin only)."""
    logger.info(f"Admin {admin.username} requesting user ID: {user_id}")

    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.debug(f"Retrieved user: {user.username}")
    return user


@router.delete("/admin/{user_id}")
async def delete_user_by_id(
    *,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
):
    """
    Delete a user by ID (admin only).

    Permanently removes a user and all associated data. Cannot be undone.
    Admins cannot delete themselves.

    Args:
        user_id: ID of the user to delete
    """
    logger.warning(
        f"Admin {admin.username} (ID={admin.id}) attempting to delete user ID: {user_id}"
    )

    # Prevent admin from deleting themselves
    if user_id == admin.id:
        logger.error(f"Admin {admin.username} attempted to delete their own account")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account",
        )

    # Find user
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Delete attempt failed: User ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}"
        )

    username = user.username
    user_role = user.role

    # Delete user (CASCADE will handle related records)
    await session.delete(user)
    await session.commit()

    logger.info(
        f"✅ User deleted by admin {admin.username}: "
        f"ID={user_id}, username={username}, role={user_role}"
    )

    return {
        "success": True,
        "user_id": user_id,
        "username": username,
        "message": f"User '{username}' deleted successfully",
    }


# ============================================================================
# Admin Routes - Statistics
# ============================================================================


@router.get("/statistics/overview")
async def get_admin_statistics_overview(
    *,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
):
    """Get high-level platform statistics (admin only)."""
    logger.info(f"Admin {admin.username} requesting statistics overview")

    # Count total users
    user_count_stmt = select(func.count(User.id))
    user_result = await session.execute(user_count_stmt)
    total_users = user_result.scalar()

    # Count documents
    doc_count_stmt = select(func.count(UserDocument.id))
    doc_result = await session.execute(doc_count_stmt)
    total_documents = doc_result.scalar()

    # Count queries
    total_queries = await query_stats_service.get_total_query_count(session)

    logger.debug(
        f"Statistics: users={total_users}, docs={total_documents}, queries={total_queries}"
    )

    return {
        "total_users": total_users,
        "total_documents": total_documents,
        "total_queries": total_queries,
        "timestamp": datetime.now(timezone.utc),
    }


@router.get("/statistics/users")
async def get_user_statistics(
    *,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
):
    """Get aggregated user statistics (admin only)."""
    logger.info(f"Admin {admin.username} requesting user statistics")

    # Users by role
    role_stmt = select(User.role, func.count(User.id)).group_by(User.role)
    role_result = await session.execute(role_stmt)
    users_by_role = {role: count for role, count in role_result.all()}

    # Users by status
    status_stmt = select(User.status, func.count(User.id)).group_by(User.status)
    status_result = await session.execute(status_stmt)
    users_by_status = {status: count for status, count in status_result.all()}

    logger.debug(f"User stats: by_role={users_by_role}, by_status={users_by_status}")

    return {
        "users_by_role": users_by_role,
        "users_by_status": users_by_status,
        "timestamp": datetime.now(timezone.utc),
    }


@router.get("/statistics/activity")
async def get_activity_statistics(
    *,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user),
    days: int = 30,
):
    """Get platform activity statistics (admin only)."""
    logger.info(
        f"Admin {admin.username} requesting activity statistics (last {days} days)"
    )

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Recent documents
    recent_docs_stmt = select(func.count(UserDocument.id)).where(
        UserDocument.created_at >= cutoff_date
    )
    recent_docs_result = await session.execute(recent_docs_stmt)
    recent_documents = recent_docs_result.scalar()

    # Recent queries
    recent_queries = await query_stats_service.get_queries_since(cutoff_date, session)

    # Active users
    active_users_count = await query_stats_service.get_active_users_count(
        cutoff_date, session
    )

    logger.debug(
        f"Activity stats: docs={recent_documents}, queries={recent_queries}, active_users={active_users_count}"
    )

    return {
        "period_days": days,
        "recent_documents_uploaded": recent_documents,
        "recent_queries": recent_queries,
        "active_users": active_users_count,
        "timestamp": datetime.now(timezone.utc),
    }
