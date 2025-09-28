from fastapi import APIRouter, Depends, BackgroundTasks, status
from app.config.rate_limits_config import limit
from app.dependencies.order_dependencies import get_order_service
from app.services.category_service import CategoryService
from app.users.auth import get_current_user
from app.pydantic_models import OrderOut

router = APIRouter(prefix="/order", tags=["order"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderOut, dependencies=[Depends(limit("MEDIUM"))])
async def create_order(
    background_tasks: BackgroundTasks,
    service: CategoryService = Depends(get_order_service),
    user=Depends(get_current_user),
):
    return await service.create_order(user, background_tasks)
