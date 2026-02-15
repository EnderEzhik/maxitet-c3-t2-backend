from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel import select, func

from src.models.user import User
from src.models.item import Item, ItemCreate, ItemUpdate

from uuid import UUID


def _apply_items_filters(stmt, title: str | None, user_id: UUID | None):
    if user_id is not None:
        stmt = stmt.where(Item.user_id == user_id)
    if title:
        title = title.strip()
        if title:
            stmt = stmt.where(Item.title.ilike(f'%{title}%'))
    return stmt


async def create_item(session: AsyncSession, user: User, item_data: ItemCreate) -> Item:
    new_item = Item(**item_data.model_dump(), user=user)
    session.add(new_item)
    await session.commit()
    return new_item


async def get_item(session: AsyncSession, item_id: UUID) -> Item | None:
    return await session.get(Item, item_id)


async def get_items_with_filters(session: AsyncSession,
    title: str | None,
    user_id: UUID | None,
    limit: int,
    offset: int
) -> tuple[list[Item], int]:
    statement = select(Item)
    statement = _apply_items_filters(statement, title, user_id)
    statement = statement.order_by(Item.title)
    statement = statement.offset(offset).limit(limit)
    result = await session.exec(statement)
    items = result.all()

    count_statement = select(func.count()).select_from(Item)
    count_statement = _apply_items_filters(count_statement, title, user_id)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    return items, count


async def update_item(
    session: AsyncSession,
    item: Item,
    item_data: ItemUpdate,
    new_user: User | None = None
    ) -> Item:
    if new_user is not None:
        item.user = new_user
    data = item_data.model_dump(exclude_unset=True, exclude={'user_id'})
    item.sqlmodel_update(data)
    session.add(item)
    await session.commit()
    return item


async def delete_item(session: AsyncSession, item: Item) -> None:
    await session.delete(item)
    await session.commit()
