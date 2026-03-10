from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker

from app.config import db_settings

engine = create_async_engine(
    url=db_settings.POSTGRES_URL,
    echo=False,
)


async def create_db_tables():
    async with engine.begin() as connection:
        from app.database.models import User #noqa F401
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session



    