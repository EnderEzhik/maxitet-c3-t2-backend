from sqlmodel import SQLModel, Field, Relationship

from uuid import UUID, uuid4

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.item import Item

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=20)
    is_active: bool = True


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    items: list["Item"] = Relationship(back_populates="user", passive_deletes="all")


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    is_active: bool | None = None


class UserOut(UserBase):
    id: UUID


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int
