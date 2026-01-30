from fastapi import APIRouter, HTTPException

from uuid import UUID

from src.database import SessionDep
from src.models.user import UserCreate, UserOut
from src.models.item import ItemCreate, ItemOut
from src.repositories import users as users_repo
from src.repositories import items as items_repo


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut)
async def create_user(session: SessionDep, user_data: UserCreate):
    return await users_repo.create_user(session, user_data)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(session: SessionDep, user_id: UUID):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.delete("/{user_id}")
async def delete_user_by_id(sessin: SessionDep, user_id: UUID):
    user = await users_repo.get_user(sessin, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    await users_repo.delete_user(sessin, user_id)
    return { "status": "deleted"}


@router.post("/{user_id}/items", response_model=ItemOut)
async def create_user_item(session: SessionDep, user_id: UUID, item_data: ItemCreate):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    new_item = await items_repo.create_item(session, user_id, item_data)
    return new_item


@router.get("/{user_id}/items")
async def get_user_items(session: SessionDep, user_id: UUID):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    item_list = await items_repo.get_list_items_by_user_id(session, user_id)
    return item_list
