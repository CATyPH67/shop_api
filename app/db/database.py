from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings_config import settings

engine = create_async_engine(settings.DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

class Base(AsyncAttrs, DeclarativeBase):
    pass__abstract__ = True