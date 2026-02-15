from fastapi import APIRouter, HTTPException, Query

from uuid import UUID

from src.database import SessionDep
from src.models.user import User, UserCreate, UserUpdate, UserOut, UsersOut
from src.models.item import ItemCreate, ItemOut, ItemsOut
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


@router.get("/", response_model=UsersOut)
async def get_users(
    session: SessionDep,
    username: str | None = Query(default=None, description="Поиск по username"),
    is_active: bool | None = Query(default=None, description="Фильтр активности"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на странице"),
    offset: int = Query(default=0, ge=0, description="Сколько записей пропустить")
):
    users, count = await users_repo.get_users_with_filters(session, username, is_active, limit, offset)
    return UsersOut(data=users, count=count)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(session: SessionDep, user_id: UUID, user_data: UserUpdate):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if user_data.username:
        existing_username = await users_repo.get_user_by_username(session, user_data.username)
        if existing_username and existing_username.id != user_id:
            raise HTTPException(status_code=409, detail="Username already exists")

    user = await users_repo.update_user(session=session, user=user, user_data=user_data)
    return user


@router.delete("/{user_id}")
async def delete_user_by_id(sessin: SessionDep, user_id: UUID):
    user = await users_repo.get_user(sessin, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    await users_repo.delete_user(sessin, user)
    return { "status": "deleted" }


@router.post("/{user_id}/items", response_model=ItemOut)
async def create_user_item(session: SessionDep, user_id: UUID, item_data: ItemCreate):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    new_item = await items_repo.create_item(session, user, item_data)
    return new_item


@router.get("/{user_id}/items", response_model=ItemsOut)
async def get_user_items(
    session: SessionDep,
    user_id: UUID,
    title: str | None = Query(default=None, description="Поиск по названию"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на странице"),
    offset: int = Query(default=0, ge=0, description="Сколько записей пропустить")
):
    user = await users_repo.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    items, count = await items_repo.get_items_with_filters(session, title, user_id, limit, offset)
    return ItemsOut(data=items, count=count)
