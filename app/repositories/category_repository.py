from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self, limit: int, offset: int
    ) -> tuple[list[Category], bool]:
        q = select(Category).order_by(Category.id.asc()).limit(limit + 1).offset(offset)
        res = await self.session.execute(q)
        categories = res.scalars().all()

        has_next = len(categories) > limit
        categories = categories[:limit]

        return categories, has_next