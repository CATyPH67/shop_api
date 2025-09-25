# app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_session
from app.db.models import Cart, CartItem, Product
from app.pydantic_models import CartItemIn, CartItemOut, CartOut
from app.users.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartOut)
async def get_cart(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user.id)
    )
    cart = result.scalars().first()

    if not cart:
        return CartOut(id=0, total_price=0.0, total_quantity=0, items=[])

    res_items = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )
    items = res_items.scalars().all()

    return CartOut(
        id=cart.id,
        total_price=cart.total_price,
        total_quantity=cart.total_quantity,
        items=[
            CartItemOut(
                id=ci.id,
                product_id=ci.product_id,
                quantity=ci.quantity,
                price=ci.price,
            )
            for ci in items
        ],
    )


@router.post("/", status_code=201, response_model=CartOut)
async def add_to_cart(
    payload: CartItemIn,
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    product = await session.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user.id)
    )
    cart = result.scalars().first()

    if cart is None:
        cart = Cart(user_id=user.id, total_price=0.0, total_quantity=0)
        session.add(cart)
        await session.flush()

    res_items = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )
    items = res_items.scalars().all()

    existing_item = next((ci for ci in items if ci.product_id == payload.product_id), None)

    if existing_item:
        existing_item.quantity += payload.quantity
        existing_item.price = product.price * existing_item.quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            price=product.price * payload.quantity,
        )
        session.add(new_item)
        items.append(new_item)

    cart.total_quantity = sum(ci.quantity for ci in items)
    cart.total_price = sum(ci.price for ci in items)

    await session.commit()

    return CartOut(
        id=cart.id,
        total_price=cart.total_price,
        total_quantity=cart.total_quantity,
        items=[
            CartItemOut(
                id=ci.id,
                product_id=ci.product_id,
                quantity=ci.quantity,
                price=ci.price,
            )
            for ci in items
        ],
    )


@router.put("/", response_model=CartOut)
async def update_cart_item(
    payload: CartItemIn,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    result = await session.execute(
        select(Cart).where(Cart.user_id == user.id)
    )
    cart = result.scalars().first()
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    res_item = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == payload.product_id)
    )
    cart_item = res_item.scalars().first()

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    if payload.quantity == 0:
        await session.delete(cart_item)
    else:
        product = await session.get(Product, payload.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        cart_item.quantity = payload.quantity
        cart_item.price = product.price * payload.quantity

    res_items = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )
    items = res_items.scalars().all()
    cart.total_quantity = sum(ci.quantity for ci in items)
    cart.total_price = sum(ci.price for ci in items)

    await session.commit()

    return CartOut(
        id=cart.id,
        total_price=cart.total_price,
        total_quantity=cart.total_quantity,
        items=[
            CartItemOut(
                id=ci.id,
                product_id=ci.product_id,
                quantity=ci.quantity,
                price=ci.price,
            )
            for ci in items
        ],
    )


@router.delete("/{item_id}", response_model=CartOut)
async def delete_cart_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    result = await session.execute(
        select(Cart).where(Cart.user_id == user.id)
    )
    cart = result.scalars().first()
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    res_item = await session.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    cart_item = res_item.scalars().first()
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await session.delete(cart_item)

    res_items = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )
    items = res_items.scalars().all()
    cart.total_quantity = sum(ci.quantity for ci in items)
    cart.total_price = sum(ci.price for ci in items)

    await session.commit()

    return CartOut(
        id=cart.id,
        total_price=cart.total_price,
        total_quantity=cart.total_quantity,
        items=[
            CartItemOut(
                id=ci.id, product_id=ci.product_id,
                quantity=ci.quantity, price=ci.price
            )
            for ci in items
        ],
    )

