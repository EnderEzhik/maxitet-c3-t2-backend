from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from src.access import AccessUser
from src.models.user import User
from src.models.item import Item, ItemCreate, ItemUpdate
import src.repositories.items as items_repo
import src.repositories.users as users_repo


async def get_items_with_filters(
    session: AsyncSession,
    current_user: AccessUser,
    title: str | None,
    limit: int,
    offset: int
) -> tuple[list[Item], int]:
    if current_user.can("items", "read"):
        user_id = None
    else:
        user_id = current_user.user.id
    return await items_repo.get_items_with_filters(session, title, user_id, limit, offset)


async def get_item_for_read(
    session: AsyncSession,
    current_user: AccessUser,
    item_id: UUID
) -> Item | None:
    item = await items_repo.get_item(session, item_id)
    if item is None:
        return None
    if current_user.can("items", "read", item.user_id):
        return item
    return None


async def get_item_for_write(
    session: AsyncSession,
    current_user: AccessUser,
    item_id: UUID
) -> Item | None:
    item = await items_repo.get_item(session, item_id)
    if item is None:
        return None
    if current_user.can("items", "write", item.user_id):
        return item
    return None


async def update_item(
    session: AsyncSession,
    item: Item,
    item_data: ItemUpdate
) -> Item:
    return await items_repo.update_item(session, item, item_data)


async def delete_item(
    session: AsyncSession,
    item: Item
) -> None:
    return await items_repo.delete_item(session, item)


async def change_item_owner(
    session: AsyncSession,
    current_user: AccessUser,
    item_id: UUID,
    new_owner_id: UUID
) -> Item | None:
    if not current_user.can("items", "write"):
        return None

    item = await items_repo.get_item(session, item_id)
    if item is None:
        return None

    new_owner = await users_repo.get_user(session, new_owner_id)
    if new_owner is None:
        return None
    return await items_repo.update_item(session, item, ItemUpdate(), new_owner)


async def create_item(
    session: AsyncSession,
    current_user: AccessUser,
    item_data: ItemCreate
) -> Item:
    owner = await session.get(User, current_user.user.id)
    return await items_repo.create_item(session, owner, item_data)
