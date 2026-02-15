from sqlmodel.ext.asyncio.session import AsyncSession

from uuid import UUID

from sqlmodel import select, func

from src.models.user import User, UserCreate, UserUpdate


def _apply_users_filters(stmt, username: str | None, is_active: bool | None):
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if username:
        username = username.strip()
        if username:
            stmt = stmt.where(User.username.ilike(f'%{username}%'))
    return stmt


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await session.exec(stmt)
    return result.first()


async def get_users_with_filters(session: AsyncSession,
    username: str | None,
    is_active: bool | None,
    limit: int,
    offset: int
) -> tuple[list[User], int]:

    statement = select(User)
    statement = _apply_users_filters(statement, username, is_active)
    statement = statement.order_by(User.username)
    statement = statement.offset(offset).limit(limit)
    result = await session.exec(statement)
    users = result.all()

    count_stmt = select(func.count()).select_from(User)
    count_stmt = _apply_users_filters(count_stmt, username, is_active)
    count_result = await session.exec(count_stmt)
    count = count_result.one()

    return users, count


async def update_user(session: AsyncSession, user: User, user_data: UserUpdate) -> User:
    user_data = user_data.model_dump(exclude_unset=True)
    user.sqlmodel_update(user_data)
    session.add(user)
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()
