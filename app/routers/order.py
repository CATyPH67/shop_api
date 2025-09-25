# app/routers/order.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_session
from app.db.models import Cart, CartItem, Order, OrderItem
from app.pydantic_models import OrderItemOut, OrderOut
from app.users.auth import get_current_user

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/", status_code=201, response_model=OrderOut)
async def create_order(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    result = await session.execute(
        select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user.id)
    )
    cart = result.scalars().first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    order = Order(
        user_id=user.id,
        total_price=cart.total_price,
        total_quantity=cart.total_quantity,
    )
    session.add(order)
    await session.flush()

    res_items = await session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = res_items.scalars().all()

    order_items = []
    for ci in items:
        oi = OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            price=ci.price,
        )
        session.add(oi)
        order_items.append(oi)

    for ci in items:
        await session.delete(ci)
    cart.total_price = 0.0
    cart.total_quantity = 0

    await session.commit()

    return OrderOut(
        id=order.id,
        total_price=order.total_price,
        total_quantity=order.total_quantity,
        created_at=order.created_at,
        items=[
            OrderItemOut(
                id=oi.id,
                product_id=oi.product_id,
                quantity=oi.quantity,
                price=oi.price,
            )
            for oi in order_items
        ],
    )
