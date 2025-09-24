from typing import Annotated
from fastapi import Depends, FastAPI
from app.auth import oauth2_scheme
from app.routers import registration, token, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# разрешение для cors
origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(token.router)
app.include_router(registration.router)

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}