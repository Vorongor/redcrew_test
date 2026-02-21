from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from src.config import get_settings

settings = get_settings()

connect_args = {}
if settings.ENVIRONMENT == "docker":
    connect_args = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
    }

engine = create_async_engine(settings.DATABASE_URL, **connect_args)


AsyncSessionLocal = async_sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    bind=engine,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session.

    This function returns an async generator yielding a new database session.
    It ensures that the session is properly closed after use.

    :return: An asynchronous generator yielding an AsyncSession instance.
    """

    async with AsyncSessionLocal() as db:
        try:
            yield db
        except SQLAlchemyError:
            await db.rollback()
            raise
        finally:
            await db.close()
