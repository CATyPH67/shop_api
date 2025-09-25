from pydantic import BaseModel, EmailStr

# user
class User(BaseModel):
    username: str
    email: EmailStr 

class SUserRegister(User):
    password: str

class SUserInDB(User):
    id: int

# token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"