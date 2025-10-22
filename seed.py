import asyncio
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_sessionmaker
from src.core.models import User
from src.core.enums import UserRole


async def create_user_if_not_exists(
    session: AsyncSession,
    username: str,
    email: str,
    password: str,
    role: UserRole,
    full_name: str
) -> User:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"User {email} already exists, skipping...")
        return existing_user

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        full_name=full_name,
        is_active=True
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    print(f"Created {role.value} user: {email}")
    return user


async def seed_test_users():
    async with async_sessionmaker() as session:
        print("Starting database seeding...")

        await create_user_if_not_exists(
            session=session,
            username="admin",
            email="admin@example.com",
            password="admin123",
            role=UserRole.ADMIN,
            full_name="Admin User"
        )

        await create_user_if_not_exists(
            session=session,
            username="worker",
            email="worker@example.com",
            password="worker123",
            role=UserRole.WORKER,
            full_name="Worker User"
        )

        print("Database seeding completed!")


async def main():
    try:
        await seed_test_users()
    except Exception as e:
        print(f"Error during seeding: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
