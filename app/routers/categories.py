from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.pydantic_models import CategoryOut

router = APIRouter(prefix="", tags=["categories"])


@router.get("/categories", response_model=List[CategoryOut], dependencies=[Depends(limit("OFTEN"))])
async def get_categories(session: AsyncSession = Depends(get_session)):
    repo = CategoryRepository(session)
    service = CategoryService(repo)
    return await service.get_categories()