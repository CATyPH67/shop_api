# app/users/dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker
from app.db.models import User

class UsersDAO:
    model = User

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            q = select(cls.model).filter_by(**filter_by)
            result = await session.execute(q)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            obj = cls.model(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
