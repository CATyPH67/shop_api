from typing import Annotated
from fastapi import Depends, FastAPI
from app.users.auth import oauth2_scheme
from app.routers import auth, categories, products
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

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}