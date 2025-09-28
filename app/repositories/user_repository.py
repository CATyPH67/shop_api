from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def add_user(self, username: str, email: str, password: str) -> User:
        user = User(username=username, email=email, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
