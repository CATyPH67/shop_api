# app/routers/products.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Product, Category, product_category
from app.db.database import async_session_maker, get_session
from app.pydantic_models import ProductOut

router = APIRouter(prefix="", tags=["products"])

@router.post("/products", response_model=List[ProductOut])
async def get_products(
    category_id: int,
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: Optional[str] = Query(None),  # "price_asc" or "price_desc"
    session: AsyncSession = Depends(get_session)
):
    q = (
        select(Product)
        .join(product_category, Product.id == product_category.c.product_id)
        .join(Category, Category.id == product_category.c.category_id)
        .where(Category.id == category_id)
        .options(joinedload(Product.categories), joinedload(Product.size))
    )   

    if min_price is not None:
        q = q.where(Product.price >= min_price)
    if max_price is not None:
        q = q.where(Product.price <= max_price)
    if sort == "price_asc":
        q = q.order_by(asc(Product.price))
    elif sort == "price_desc":
        q = q.order_by(desc(Product.price))

    res = await session.execute(q)
    prods = res.scalars().unique().all()

    out = []
    for p in prods:
        cat_names = [c.name for c in p.categories]
        size_name = p.size.name if p.size else None
        out.append(ProductOut(
            id=p.id, name=p.name, description=p.description,
            image=p.image, price=p.price, size=size_name, categories=cat_names
        ))
    return out

@router.get("/product/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(
        select(Product)
        .options(joinedload(Product.categories), joinedload(Product.size))
        .where(Product.id == product_id)
    )
    p = res.unique().scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    cat_names = [c.name for c in p.categories]
    size_name = p.size.name if p.size else None
    return ProductOut(
        id=p.id, name=p.name, 
        description=p.description,
        image=p.image, 
        price=p.price, size=size_name, 
        categories=cat_names
    )
