import secrets
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth import oauth
from app.db.database import get_session
from app.db.models import User
from app.services.email import send_email
from app.users.auth import create_access_token, get_password_hash, verify_password
from app.pydantic_models import SUserInDB, SUserRegister, Token
from app.users.dao import UsersDAO
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: SUserRegister) -> SUserInDB:
# async def register_user(form_data: OAuth2PasswordRequestForm = Depends()) -> SUserInDB:
    exists = await UsersDAO.find_one_or_none(email=user_data.email)
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с такой почтой уже существует")
    
    exists = await UsersDAO.find_one_or_none(username=user_data.username)
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")

    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    user = await UsersDAO.add(**user_dict)
    return SUserInDB(id=user.id, username=user.username, email=user.email)

@router.post("/token", response_model=Token)
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await UsersDAO.find_one_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/yandex/login")
async def yandex_login(request: Request):
    return await oauth.yandex.authorize_redirect(request, settings.YANDEX_REDIRECT_URI)


@router.get("/yandex/callback")
async def yandex_callback(
    background_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Token:
    token = await oauth.yandex.authorize_access_token(request)
    user_info = await oauth.yandex.get("info", token=token)
    data = user_info.json()

    yandex_email = data.get("default_email")
    yandex_username = data.get("login") or data.get("real_name")

    if not yandex_email:
        raise HTTPException(status_code=400, detail="Email не предоставлен Яндексом")

    # Проверяем наличие пользователя
    user_by_email = await UsersDAO.find_one_or_none(email=yandex_email)
    user_by_username = await UsersDAO.find_one_or_none(username=yandex_username)

    if user_by_email and user_by_email.username != yandex_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")
    
    if user_by_username and user_by_email.email != yandex_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с такой почтой уже существует")
    
    if not user_by_email and not user_by_username:
        # Не зарегистрирован
        generated_password = secrets.token_urlsafe(12)
        hashed_password = get_password_hash(generated_password)

        new_user = User(
            username=yandex_username,
            email=yandex_email,
            password=hashed_password,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Отправляем пароль на email
        background_tasks.add_task(
            send_email,
            new_user.email,
            "Ваш пароль для входа в Shop API", 
            f"""
            <h2>Здравствуйте, {yandex_username}!</h2>
            <p>Вы зарегистрировались через Яндекс.</p>
            <p>Ваш пароль: {generated_password}</p>
            <p>Вы можете использовать его для входа через обычную форму авторизации.</p>
            """
        )

        access_token = create_access_token(data={"sub": str(new_user.id)})
        return Token(access_token=access_token, token_type="bearer")

    # Уже зарегистрирован
    access_token = create_access_token(data={"sub": str(user_by_username.id)})
    return Token(access_token=access_token, token_type="bearer")   