from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from src.models.user import User, UserCreate


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()
