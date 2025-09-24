from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import fake_users_db, get_password_hash

router = APIRouter(tags=["registartion"])

@router.post("/registration")
async def registrate_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if form_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User is already registrated!")
    else:
        password_hash = get_password_hash(form_data.password)
        fake_users_db[form_data.username] = {
            "username": form_data.username,
            "hashed_password": password_hash,
            "disabled": False,
        }
        return {"user was registrated successfully"}