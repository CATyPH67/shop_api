from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from app.routers import auth, cart, categories, order, products
from app.config.settings_config import settings 
from app.config.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = redis.from_url(settings.REDIS_DSN, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)
    logger.info("FastAPI app started, Redis and RateLimiter initialized")

    yield  # тут приложение работает

    await FastAPILimiter.close()
    logger.info("FastAPI app shutdown, Redis connection closed")


app = FastAPI(title="Shop API", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# # CORS (можно включить при необходимости)
# origins = ["http://localhost:5173"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Роутеры
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(order.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception(
            "Unhandled error during request",
            extra={"extra_fields": {"method": request.method, "url": str(request.url)}}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
