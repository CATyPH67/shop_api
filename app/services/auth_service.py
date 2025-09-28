import secrets
from fastapi import HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.user_repository import UserRepository
from app.users.auth import create_access_token, get_password_hash, verify_password
from app.pydantic_models import SUserInDB, SUserRegister, Token
from app.services.email_service import send_email
from app.config.settings_config import settings
from app.oauth import oauth
from app.config.logging_config import logger


class AuthService:
    def __init__(self, userRepo: UserRepository):
        self.userRepo = userRepo

    async def register_user(self, user_data: SUserRegister) -> SUserInDB:
        logger.info(
            "Register attempt",
            extra={"extra_fields": {"username": user_data.username, "email": user_data.email}}
        )

        if await self.userRepo.get_by_email(user_data.email):
            logger.warning(
                "Registration failed: email already exists",
                extra={"extra_fields": {"email": user_data.email}}
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that email already exist")

        if await self.userRepo.get_by_username(user_data.username):
            logger.warning(
                "Registration failed: username already exists",
                extra={"extra_fields": {"username": user_data.username}}
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that name already exist")

        hashed_password = get_password_hash(user_data.password)
        user = await self.userRepo.add_user(user_data.username, user_data.email, hashed_password)
        logger.info(
            "User registered successfully",
            extra={"extra_fields": {"user_id": user.id, "username": user.username, "email": user.email}}
        )
        return SUserInDB(id=user.id, username=user.username, email=user.email, role=user.role)

    async def login(self, form_data: OAuth2PasswordRequestForm) -> Token:
        logger.info(
            "Login attempt",
            extra={"extra_fields": {"username": form_data.username}}
        )

        user = await self.userRepo.get_by_username(form_data.username)
        if not user:
            logger.warning(
                "Login failed: username not found",
                extra={"extra_fields": {"username": form_data.username}}
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username")

        if not verify_password(form_data.password, user.password):
            logger.warning(
                "Login failed: invalid password",
                extra={"extra_fields": {"username": form_data.username}}
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")

        access_token = create_access_token({"sub": str(user.id)})
        logger.info(
            "Login successful",
            extra={"extra_fields": {"user_id": user.id, "username": user.username}}
        )
        return Token(access_token=access_token, token_type="bearer")

    async def yandex_login(self, request: Request):
        logger.info("Redirecting user to Yandex OAuth")
        return await oauth.yandex.authorize_redirect(request, settings.YANDEX_REDIRECT_URI)

    async def yandex_callback(self, background_tasks: BackgroundTasks, request: Request) -> Token:
        logger.info("Yandex OAuth callback received")
        try:
            token = await oauth.yandex.authorize_access_token(request)
            user_info = await oauth.yandex.get("info", token=token)
            data = user_info.json()

            yandex_email = data.get("default_email")
            yandex_username = data.get("login") or data.get("real_name")

            if not yandex_email:
                logger.error(
                    "Yandex OAuth callback error: no email received",
                    extra={"extra_fields": {"yandex_username": yandex_username}}
                )
                raise HTTPException(status_code=400, detail="No mail received from Yandex")

            user_by_email = await self.userRepo.get_by_email(yandex_email)
            user_by_username = await self.userRepo.get_by_username(yandex_username)

            if user_by_email and user_by_email.username != yandex_username:
                logger.warning(
                    "Conflict during Yandex login: username exists for another email",
                    extra={"extra_fields": {"yandex_username": yandex_username, "email": yandex_email}}
                )
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that name already exist")

            if user_by_username and user_by_email and user_by_email.email != yandex_email:
                logger.warning(
                    "Conflict during Yandex login: email exists for another username",
                    extra={"extra_fields": {"yandex_username": yandex_username, "email": yandex_email}}
                )
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that email already exist")

            if not user_by_email and not user_by_username:
                generated_password = secrets.token_urlsafe(12)
                hashed_password = get_password_hash(generated_password)
                new_user = await self.userRepo.add_user(yandex_username, yandex_email, hashed_password)

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

                user_id = str(new_user.id)
                logger.info(
                    "New user created via Yandex OAuth",
                    extra={"extra_fields": {"user_id": new_user.id, "username": yandex_username, "email": yandex_email}}
                )
            else:
                user_id = str(user_by_username.id)
                logger.info(
                    "Existing user logged in via Yandex OAuth",
                    extra={"extra_fields": {"user_id": user_by_username.id, "username": user_by_username.username, "email": user_by_username.email}}
                )

            access_token = create_access_token(data={"sub": user_id})
            return Token(access_token=access_token, token_type="bearer")

        except Exception:
            logger.exception("Unexpected error during Yandex OAuth callback")
            raise HTTPException(status_code=500, detail="Internal server error")