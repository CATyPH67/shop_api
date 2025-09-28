from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Size


class SizeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Size] | None:
        res = await self.session.execute(select(Size))
        return res.scalars().all()
    
    async def get_size_by_id(self, size_id: int) -> Size | None:
        result = await self.session.execute(select(Size).where(Size.id == size_id))
        return result.scalar_one_or_none()