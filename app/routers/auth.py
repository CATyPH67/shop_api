from fastapi import APIRouter, Depends, BackgroundTasks, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies.auth_dependencies import get_auth_service
from app.services.auth_service import AuthService
from app.pydantic_models import SUserInDB, SUserRegister, Token

from app.utils.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("RARE"))])
async def register_user(user_data: SUserRegister, service: AuthService = Depends(get_auth_service)) -> SUserInDB:
    return await service.register_user(user_data)


@router.post("/token", response_model=Token, dependencies=[Depends(rate_limit("RARE"))])
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)) -> Token:
    return await service.login(form_data)


@router.get("/yandex/login", dependencies=[Depends(rate_limit("RARE"))])
async def yandex_login(request: Request, service: AuthService = Depends(get_auth_service)):
    return await service.yandex_login(request)


@router.get("/yandex/callback", dependencies=[Depends(rate_limit("RARE"))])
async def yandex_callback(background_tasks: BackgroundTasks, request: Request, service: AuthService = Depends(get_auth_service)) -> Token:
    return await service.yandex_callback(background_tasks, request)