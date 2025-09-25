from authlib.integrations.starlette_client import OAuth
from app.config import settings

oauth = OAuth()

oauth.register(
    name="yandex",
    client_id=settings.YANDEX_CLIENT_ID,
    client_secret=settings.YANDEX_CLIENT_SECRET,
    access_token_url="https://oauth.yandex.ru/token",
    authorize_url="https://oauth.yandex.ru/authorize",
    api_base_url="https://login.yandex.ru/info",
    client_kwargs={"scope": "login:email login:info"},
)