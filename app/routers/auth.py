from fastapi import APIRouter, Depends, BackgroundTasks, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.pydantic_models import SUserInDB, SUserRegister, Token
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(limit("RARE"))])
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session)) -> SUserInDB:
    service = AuthService(UserRepository(session))
    return await service.register_user(user_data)


@router.post("/token", response_model=Token, dependencies=[Depends(limit("RARE"))])
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)) -> Token:
    service = AuthService(UserRepository(session))
    return await service.login(form_data)


@router.get("/yandex/login", dependencies=[Depends(limit("RARE"))])
async def yandex_login(request: Request, session: AsyncSession = Depends(get_session)):
    service = AuthService(UserRepository(session))
    return await service.yandex_login(request)


@router.get("/yandex/callback", dependencies=[Depends(limit("RARE"))])
async def yandex_callback(background_tasks: BackgroundTasks, request: Request, session: AsyncSession = Depends(get_session)) -> Token:
    service = AuthService(UserRepository(session))
    return await service.yandex_callback(background_tasks, request)