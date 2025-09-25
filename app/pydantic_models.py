from datetime import datetime
from typing import List, Optional
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

# Product
class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    image: str
    price: float
    size: str
    categories: List[str]

# Category
class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    subcategories: List["CategoryOut"] = []

    class Config:
        orm_mode = True

# Cart
class CartItemIn(BaseModel):
    product_id: int
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float


class CartOut(BaseModel):
    id: int
    total_price: float
    total_quantity: int
    items: List[CartItemOut]

# Order
class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    total_price: float
    total_quantity: int
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True