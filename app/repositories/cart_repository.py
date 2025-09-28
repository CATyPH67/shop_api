from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Cart, CartItem


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        result = await self.session.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        return result.scalars().first()

    async def get_items(self, cart_id: int) -> list[CartItem]:
        result = await self.session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .options(selectinload(CartItem.product))
        )
        return result.scalars().all()

    async def get_item_by_product(self, cart_id: int, product_id: int) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .options(selectinload(CartItem.product))
        )
        return result.scalars().first()

    async def get_item_by_id(self, cart_id: int, item_id: int) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.id == item_id)
            .options(selectinload(CartItem.product))
        )
        return result.scalars().first()

    async def create_cart(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id, total_price=0.0, total_quantity=0)
        self.session.add(cart)
        await self.session.flush()
        return cart

    async def add_item(self, cart_id: int, product_id: int, quantity: int, price: float) -> CartItem:
        item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, price=price)
        self.session.add(item)
        await self.session.flush()
        return item

    async def delete_item(self, item: CartItem):
        await self.session.delete(item)

    async def clear_cart(self, cart: Cart, items: list[CartItem]):
        for ci in items:
            await self.session.delete(ci)
        cart.total_price = 0.0
        cart.total_quantity = 0

    async def commit(self):
        await self.session.commit()