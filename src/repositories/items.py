from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select

from src.models.item import Item, ItemCreate

from uuid import UUID


async def create_item(session: AsyncSession, user_id: UUID, item_data: ItemCreate) -> Item:
    new_item = Item(**item_data.model_dump(), user_id=user_id)
    session.add(new_item)
    await session.commit()
    return new_item


async def get_item(session: AsyncSession, item_id: UUID) -> Item | None:
    return await session.get(Item, item_id)


async def get_list_items_by_user_id(session: AsyncSession, user_id: UUID) -> list[Item]:
    stmt = select(Item).where(Item.user_id == user_id)
    result = await session.execute(stmt)
    return result.all()


async def delete_item(session: AsyncSession, item: Item) -> None:
    await session.delete(item)
    await session.commit()
