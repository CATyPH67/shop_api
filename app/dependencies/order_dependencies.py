from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


async def get_order_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    orderRepo = OrderRepository(session)
    cartRepo = CartRepository(session)
    return OrderService(orderRepo, cartRepo)