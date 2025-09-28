from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.repositories.cart_repository import CartRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.services.cart_service import CartService
from app.services.category_service import CategoryService


async def get_category_service(session: AsyncSession = Depends(get_session)) -> CartService:
    categRepo = CategoryRepository(session)
    return CategoryService(categRepo)