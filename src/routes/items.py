from fastapi import APIRouter, HTTPException

from uuid import UUID

from src.database import SessionDep
from src.models.item import ItemOut
import src.repositories.items as items_repo


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_id}", response_model=ItemOut)
async def get_item_by_id(session: SessionDep, item_id: UUID):
    item = await items_repo.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@router.delete("/{item_id}")
async def delete_item_by_id(session: SessionDep, item_id: UUID):
    item = await items_repo.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    await items_repo.delete_item(session, item)
    return { "status": "deleted"}
