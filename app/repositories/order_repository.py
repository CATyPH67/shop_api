from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Cart, CartItem, Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        result = await self.session.execute(
            select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user_id)
        )
        return result.scalars().first()

    async def get_cart_items(self, cart_id: int):
        result = await self.session.execute(select(CartItem).where(CartItem.cart_id == cart_id))
        return result.scalars().all()

    async def create_order(self, user_id: int, total_price: float, total_quantity: int) -> Order:
        order = Order(user_id=user_id, total_price=total_price, total_quantity=total_quantity)
        self.session.add(order)
        await self.session.flush()
        return order

    async def add_order_item(self, order_id: int, product_id: int, quantity: int, price: float) -> OrderItem:
        oi = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        self.session.add(oi)
        return oi

    async def clear_cart(self, cart: Cart, items: list[CartItem]):
        for ci in items:
            await self.session.delete(ci)
        cart.total_price = 0.0
        cart.total_quantity = 0

    async def commit(self):
        await self.session.commit()
