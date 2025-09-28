from fastapi import APIRouter, Depends, Query
from app.dependencies.categoties_dependencies import get_category_service
from app.services.category_service import CategoryService
from app.pydantic_models import PaginatedCategories
from app.config.settings_config import settings
from app.utils.rate_limit import rate_limit

router = APIRouter(prefix="", tags=["categories"])


@router.get(
    "/categories",
    response_model=PaginatedCategories,
    dependencies=[Depends(rate_limit("OFTEN"))],
)
async def get_categories(
    limit: int = Query(10, ge=1, le=settings.LIMIT_MAXIMUM),
    offset: int = Query(0, ge=0),
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_categories(limit, offset)