from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.dependencies.products_dependencies import get_product_service
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.pydantic_models import PaginatedProducts, ProductIn, ProductOut
from app.users.auth import get_current_admin
from app.config.settings_config import settings

router = APIRouter(prefix="", tags=["products"])

@router.post(
    "/product",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit("MEDIUM")), Depends(get_current_admin)]
)
async def create_product(
    payload: ProductIn,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(payload)


@router.post(
    "/products",
    response_model=PaginatedProducts,
    dependencies=[Depends(limit("OFTEN"))]
)
async def get_products(
    category_id: int,
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=settings.LIMIT_MAXIMUM),
    offset: int = Query(0, ge=0),
    service: ProductService = Depends(get_product_service),
):
    return await service.get_products(category_id, min_price, max_price, sort, limit, offset)


@router.get("/product/{product_id}", response_model=ProductOut, dependencies=[Depends(limit("OFTEN"))])
async def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return await service.get_product(product_id)
