from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.item import Item


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=20)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(SQLModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    is_active: bool | None = None


class UserOut(UserBase):
    id: UUID


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="user", passive_deletes="all")
