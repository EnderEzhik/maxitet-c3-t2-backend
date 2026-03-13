from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlmodel.ext.asyncio.session import AsyncSession


ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/todo"

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionMaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
