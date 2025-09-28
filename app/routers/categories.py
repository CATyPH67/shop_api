from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.pydantic_models import PaginatedCategories
from app.config.settings_config import settings

router = APIRouter(prefix="", tags=["categories"])


@router.get(
    "/categories",
    response_model=PaginatedCategories,
    dependencies=[Depends(limit("OFTEN"))],
)
async def get_categories(
    limit: int = Query(10, ge=1, le=settings.LIMIT_MAXIMUM),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    repo = CategoryRepository(session)
    service = CategoryService(repo)
    return await service.get_categories(limit, offset)