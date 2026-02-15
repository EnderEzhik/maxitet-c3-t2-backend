from fastapi import APIRouter, HTTPException, Query

from uuid import UUID

from src.database import SessionDep
from src.models.item import ItemUpdate, ItemOut, ItemsOut
import src.repositories.users as users_repo
import src.repositories.items as items_repo


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsOut)
async def get_items(
    session: SessionDep,
    title: str | None = Query(default=None, description="Поиск по title"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на странице"),
    offset: int = Query(default=0, ge=0, description="Сколько записей пропустить")
):
    items, count = await items_repo.get_items_with_filters(session, title, None, limit, offset)
    return ItemsOut(data=items, count=count)


@router.get("/{item_id}", response_model=ItemOut)
async def get_item_by_id(session: SessionDep, item_id: UUID):
    item = await items_repo.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(session: SessionDep, item_id: UUID, item_data: ItemUpdate):
    item = await items_repo.get_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    payload = item_data.model_dump(exclude_unset=True)
    new_user = None

    if "user_id" in payload:
        if item_data.user_id is None:
            raise HTTPException(status_code=422, detail="user_id cannot be null")

        new_user = await users_repo.get_user(session, item_data.user_id)
        if new_user is None:
            raise HTTPException(status_code=404, detail="User not found")

    updated_item = await items_repo.update_item(
        session=session,
        item=item,
        item_data=item_data,
        new_user=new_user
    )
    return updated_item


@router.delete("/{item_id}")
async def delete_item_by_id(session: SessionDep, item_id: UUID):
    item = await items_repo.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    await items_repo.delete_item(session, item)
    return { "status": "deleted"}
