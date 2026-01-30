from sqlmodel import SQLModel, Field

from uuid import UUID, uuid4


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, min_length=1, max_length=128)


class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)


class ItemCreate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: UUID
    user_id: UUID


class ItemsOut(SQLModel):
    data: list[ItemOut]
    count: int


class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=128)
