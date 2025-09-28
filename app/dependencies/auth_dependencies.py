from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.config.settings_config import settings
from app.config.logging_config import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(session))

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    # Получение текущего пользователя из токена
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    repo = UserRepository(session)
    user = await repo.get_by_id(int(user_id)) if hasattr(repo, "get_by_id") else None
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(user=Depends(get_current_user)):
    # Проверка роли администратора
    if user.role != "admin":
        logger.warning(
            "Attempt without the admin role",
            extra={"extra_fields": {"username": user.username}},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights",
        )
    return user