from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Size


class SizeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Size] | None:
        res = await self.session.execute(select(Size))
        return res.scalars().all()