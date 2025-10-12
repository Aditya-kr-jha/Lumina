# Backend/app/scripts/create_admin.py
import asyncio
from sqlmodel import select

from app.db.session import get_async_session, create_db_and_tables_async
from app.models.db_models import User
from app.models.schemas import UserRole, UserStatus
from app.auth import hash_password


async def create_initial_admin():
    """Create the first admin user."""
    # Create tables using your existing function
    await create_db_and_tables_async()

    # Use your existing session generator
    async for session in get_async_session():
        statement = select(User).where(User.role == UserRole.ADMIN)
        result = await session.execute(statement)
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin user already exists!")
            return

        admin_user = User(
            username="admin",
            email="ngc.aditya010@gmail.com",
            hashed_password=hash_password("aditya123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )

        session.add(admin_user)
        await session.commit()
        print(f"Admin user created: {admin_user.username}")
        break


if __name__ == "__main__":
    asyncio.run(create_initial_admin())
