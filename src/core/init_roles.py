import asyncio

from sqlmodel import select

from src.core.config import settings
from src.database import AsyncSessionMaker
from src.models.role import Role, RoleName, UserRoles
from src.models.user import User, UserCreate
import src.repositories.users as repo_user


async def create_roles_and_admin():
    if not settings.FIRST_ADMIN_USERNAME:
        raise SystemExit("FIRST_ADMIN_USERNAME can not be empty")
    if not settings.FIRST_ADMIN_PASSWORD:
        raise SystemExit("FIRST_ADMIN_PASSWORD can not be empty")

    async with AsyncSessionMaker() as session:
        roles = (await session.exec(select(Role))).all()
        roles_by_name = { r.name for r in roles }
        if RoleName.USER.value not in roles_by_name:
            session.add(Role(name=RoleName.USER.value, description="Default user role"))
        if RoleName.ADMIN.value not in roles_by_name:
            session.add(Role(name=RoleName.ADMIN.value, description="Admin role"))
        await session.commit()

        role_admin = (
            await session.exec(select(Role).where(Role.name == RoleName.ADMIN.value))
        ).one()

        admin_user = (
            await session.exec(select(User).where(User.username == settings.FIRST_ADMIN_USERNAME))
        ).first()

        if not admin_user:
            admin_data = UserCreate(
                username=settings.FIRST_ADMIN_USERNAME,
                password=settings.FIRST_ADMIN_PASSWORD
            )
            admin_user = await repo_user.create_user(session, admin_data)

        link = (
            await session.exec(select(UserRoles).where(
                (UserRoles.user_id == admin_user.id) & (UserRoles.role_id == role_admin.id)
                )
            )
        ).first()

        if not link:
            session.add(UserRoles(user_id=admin_user.id, role_id=role_admin.id))
            await session.commit()


if __name__ == "__main__":
    asyncio.run(create_roles_and_admin())
