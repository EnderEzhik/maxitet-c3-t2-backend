from sqlalchemy import Column, Integer, String, Boolean

from pydantic import BaseModel, Field, ConfigDict

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int = Field(...)
    model_config = ConfigDict(from_attributes=True)
