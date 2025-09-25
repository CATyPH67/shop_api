from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.users.auth import create_access_token, get_password_hash, verify_password
from app.pydantic_models import SUserInDB, SUserRegister, Token
from app.users.dao import UsersDAO

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/", status_code=201)
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