from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.rate_limits_config import limit
from app.db.database import get_session
from app.dependencies.cart_dependencies import get_cart_service
from app.users.auth import get_current_user
from app.services.cart_service import CartService
from app.pydantic_models import CartItem, CartItemFields, CartOut

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartOut, dependencies=[Depends(limit("MEDIUM"))])
async def get_cart(service: CartService = Depends(get_cart_service), user=Depends(get_current_user)):
    return await service.get_cart(user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CartOut, dependencies=[Depends(limit("MEDIUM"))])
async def add_to_cart(payload: CartItem, service: CartService = Depends(get_cart_service), user=Depends(get_current_user)):
    return await service.add_to_cart(user, payload)


@router.put("/", response_model=CartOut, dependencies=[Depends(limit("MEDIUM"))])
async def update_cart_item(item_id: int,payload: CartItemFields, service: CartService = Depends(get_cart_service), user=Depends(get_current_user)):
    return await service.update_cart_item(item_id, user, payload)


@router.delete("/{item_id}", response_model=CartOut, dependencies=[Depends(limit("MEDIUM"))])
async def delete_cart_item(item_id: int, service: CartService = Depends(get_cart_service), user=Depends(get_current_user)):
    return await service.delete_cart_item(user, item_id)
