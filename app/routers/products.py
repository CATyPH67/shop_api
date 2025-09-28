from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.pydantic_models import ProductIn, ProductOut
from app.users.auth import get_current_admin

router = APIRouter(prefix="", tags=["products"])

@router.post(
    "/product",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit("MEDIUM")), Depends(get_current_admin)]
)
async def create_product(
    payload: ProductIn,
    session: AsyncSession = Depends(get_session),
):
    repo = ProductRepository(session)
    service = ProductService(repo)
    return await service.create_product(payload)


@router.post("/products", response_model=List[ProductOut], dependencies=[Depends(limit("OFTEN"))])
async def get_products(
    category_id: int,
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    repo = ProductRepository(session)
    service = ProductService(repo)
    return await service.get_products(category_id, min_price, max_price, sort)


@router.get("/product/{product_id}", response_model=ProductOut, dependencies=[Depends(limit("OFTEN"))])
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    repo = ProductRepository(session)
    service = ProductService(repo)
    return await service.get_product(product_id)
