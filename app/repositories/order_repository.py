from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, user_id: int, total_price: float, total_quantity: int) -> Order:
        order = Order(user_id=user_id, total_price=total_price, total_quantity=total_quantity)
        self.session.add(order)
        await self.session.flush()
        return order

    async def add_order_item(self, order_id: int, product_id: int, quantity: int, price: float) -> OrderItem:
        oi = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        self.session.add(oi)
        return oi

    async def commit(self):
        await self.session.commit()