from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlmodel.ext.asyncio.session import AsyncSession


ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/TempNameProject"

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionMaker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionMaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
