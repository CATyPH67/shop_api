from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from app.dependencies.products_dependencies import get_product_service
from app.services.product_service import ProductService
from app.pydantic_models import PaginatedProducts, ProductIn, ProductOut
from app.dependencies.auth_dependencies import get_current_admin
from app.config.settings_config import settings
from app.utils.rate_limit import rate_limit

router = APIRouter(prefix="", tags=["products"])

@router.post(
    "/product",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("MEDIUM")), Depends(get_current_admin)]
)
async def create_product(
    payload: ProductIn,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(payload)


@router.post(
    "/products",
    response_model=PaginatedProducts,
    dependencies=[Depends(rate_limit("OFTEN"))]
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


@router.get("/product/{product_id}", response_model=ProductOut, dependencies=[Depends(rate_limit("OFTEN"))])
async def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return await service.get_product(product_id)
