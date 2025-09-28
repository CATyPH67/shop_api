from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category] | None:
        res = await self.session.execute(select(Category))
        return res.scalars().all()