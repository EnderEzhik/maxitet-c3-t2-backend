from sqlmodel import SQLModel, Field

from uuid import UUID, uuid4


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=20)
    is_active: bool = True


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, default_factory=uuid4)


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: UUID
