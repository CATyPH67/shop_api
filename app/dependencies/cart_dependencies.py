from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.services.cart_service import CartService


async def get_cart_service(session: AsyncSession = Depends(get_session)) -> CartService:
    cart_repo = CartRepository(session)
    prod_repo = ProductRepository(session)
    return CartService(cart_repo, prod_repo)