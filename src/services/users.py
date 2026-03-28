from sqlmodel.ext.asyncio.session import AsyncSession

from src.access import AccessUser
from src.models.user import User, UserUpdate
import src.repositories.users as users_repo


async def get_me(current_user: AccessUser) -> User:
    return current_user.user


async def update_me(
    session: AsyncSession,
    current_user: AccessUser,
    user_data: UserUpdate
) -> User:
    if user_data.username:
        existing_user = await users_repo.get_user_by_username(session, user_data.username)
    if existing_user and existing_user.id != current_user.user.id:
        raise ValueError("Username already exists")

    user = await session.get(User, current_user.user.id)
    return await users_repo.update_user(session, user, user_data)
