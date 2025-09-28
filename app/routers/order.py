from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.users.auth import get_current_user
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.pydantic_models import OrderOut

router = APIRouter(prefix="/order", tags=["order"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderOut, dependencies=[Depends(limit("MEDIUM"))])
async def create_order(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    repo = OrderRepository(session)
    service = OrderService(repo)
    return await service.create_order(user, background_tasks)
