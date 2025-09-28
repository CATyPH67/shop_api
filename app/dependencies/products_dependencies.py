from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.size_repository import SizeRepository
from app.services.product_service import ProductService


async def get_product_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    prodRepo = ProductRepository(session)
    sizeRepo = SizeRepository(session)
    categRepo = CategoryRepository(session)
    return ProductService(prodRepo, sizeRepo, categRepo)