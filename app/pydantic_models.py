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
    role: str

# token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Product

class Product(BaseModel):
    name: str
    description: str
    image: str 
    price: float

class ProductIn(Product):
    size_id: int
    category_ids: List[int]

class ProductOut(Product):
    id: int
    size: str
    categories: List[str]

# Category
class Category(BaseModel):
    id: int
    name: str
class CategoryOut(Category):
    parent_id: Optional[int]
    subcategories: List["CategoryOut"] = []

    class Config:
        orm_mode = True

# Cart
class CartItem(BaseModel):
    product_id: int
    quantity: int
class CartItemOut(CartItem):
    id: int
    price: float

class CartItemFields(CartItem):
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