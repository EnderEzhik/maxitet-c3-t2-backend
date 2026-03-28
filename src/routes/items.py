from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Security

from src.access import AccessUser
from src.deps import SessionDep, get_current_user
from src.models.item import ItemCreate, ItemUpdate, ItemOut, ItemsOut, ItemOwnerUpdate
import src.services.items as items_service


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsOut)
async def get_items(
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:read:own"])],
    session: SessionDep,
    title: str | None = Query(default=None, description="Поиск по title"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на странице"),
    offset: int = Query(default=0, ge=0, description="Сколько записей пропустить")
):
    items, count = await items_service.get_items_with_filters(session, current_user, title, limit, offset)
    return ItemsOut(data=items, count=count)


@router.get("/{item_id}", response_model=ItemOut)
async def get_item_by_id(
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:read:own"])],
    session: SessionDep,
    item_id: UUID
):
    item = await items_service.get_item_for_read(session, current_user, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@router.patch("/{item_id}", response_model=ItemOut)
async def change_item(
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:write:own"])],
    session: SessionDep,
    item_id: UUID,
    item_data: ItemUpdate
):
    item = await items_service.get_item_for_write(session, current_user, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    updated_item = await items_service.update_item(
        session,
        item,
        item_data
    )
    return updated_item


@router.patch("/{item_id}/owner", response_model=ItemOut)
async def change_item_owner(
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:write:own"])],
    session: SessionDep,
    item_id: UUID,
    owner_data: ItemOwnerUpdate
):
    updated = await items_service.change_item_owner(session, current_user, item_id, owner_data.user_id)

    if updated is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    return updated


@router.delete("/{item_id}")
async def delete_item_by_id(
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:write:own"])],
    session: SessionDep,
    item_id: UUID
):
    item = await items_service.get_item_for_write(session, current_user, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    await items_service.delete_item(session, item)
    return { "status": "deleted"}


@router.post("/", response_model=ItemOut)
async def create_item(
    session: SessionDep,
    current_user: Annotated[AccessUser, Security(get_current_user, scopes=["items:write:own"])],
    item_data: ItemCreate
):
    return await items_service.create_item(session, current_user, item_data)
