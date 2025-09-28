from fastapi import HTTPException, status
from app.db.models import CartItem
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.pydantic_models import CartItem, CartItemFields, CartItemOut, CartOut
from app.config.logging_config import logger


class CartService:
    def __init__(self, cartRepo: CartRepository, prodRepo: ProductRepository):
        self.cartRepo = cartRepo
        self.prodRepo = prodRepo

    async def _build_cart_out(self, cart, items) -> CartOut:
        return CartOut(
            id=cart.id,
            total_price=cart.total_price,
            total_quantity=cart.total_quantity,
            items=[
                CartItemOut(
                    id=ci.id,
                    product_id=ci.product_id,
                    quantity=ci.quantity,
                    price=ci.price,
                )
                for ci in items
            ],
        )
    
    async def update_cart_totals(self, cart: CartOut, items: list[CartItem]):
        cart.total_quantity = sum(ci.quantity for ci in items)
        cart.total_price = sum(ci.price for ci in items)
        await self.cartRepo.commit()
        logger.info(
            "Cart totals updated",
            extra={"extra_fields": {"cart_id": cart.id, "total_quantity": cart.total_quantity, "total_price": cart.total_price}}
        )

    async def get_cart(self, user) -> CartOut:
        cart = await self.cartRepo.get_cart_with_items(user.id)
        if not cart:
            logger.info("Empty cart returned", extra={"extra_fields": {"user_id": user.id}})
            return CartOut(id=0, total_price=0.0, total_quantity=0, items=[])
        items = await self.cartRepo.get_items(cart.id)
        logger.info("Cart retrieved", extra={"extra_fields": {"user_id": user.id, "cart_id": cart.id}})
        return await self._build_cart_out(cart, items)

    async def add_to_cart(self, user, payload: CartItem) -> CartOut:
        logger.info(
            "Add to cart attempt",
            extra={"extra_fields": {"user_id": user.id, "product_id": payload.product_id, "quantity": payload.quantity}}
        )

        if payload.quantity == 0:
            logger.warning(
                "Add to cart failed: quantity zero",
                extra={"extra_fields": {"user_id": user.id, "product_id": payload.product_id}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity is zero")

        product = await self.prodRepo.get_product(payload.product_id)
        if not product:
            logger.warning(
                "Add to cart failed: product not found",
                extra={"extra_fields": {"user_id": user.id, "product_id": payload.product_id}}
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        cart = await self.cartRepo.get_cart_with_items(user.id)
        if not cart:
            cart = await self.cartRepo.create_cart(user.id)
            logger.info("New cart created", extra={"extra_fields": {"user_id": user.id, "cart_id": cart.id}})

        items = await self.cartRepo.get_items(cart.id)
        existing_item = await self.cartRepo.get_item_by_product(cart.id, payload.product_id)

        if existing_item:
            existing_item.quantity += payload.quantity
            existing_item.price = product.price * existing_item.quantity
            logger.info(
                "Cart item updated",
                extra={"extra_fields": {"cart_id": cart.id, "product_id": payload.product_id, "new_quantity": existing_item.quantity}}
            )
        else:
            new_item = await self.cartRepo.add_item(
                cart.id, payload.product_id, payload.quantity, product.price * payload.quantity
            )
            items.append(new_item)
            logger.info(
                "New item added to cart",
                extra={"extra_fields": {"cart_id": cart.id, "product_id": payload.product_id, "quantity": payload.quantity}}
            )

        await self.update_cart_totals(cart, items)
        return await self._build_cart_out(cart, items)
    
    async def update_cart_item(self, item_id: int, user, payload: CartItemFields) -> CartOut:
        cart = await self.cartRepo.get_cart_with_items(user.id)
        if not cart:
            logger.warning("Update cart item failed: cart not found", extra={"extra_fields": {"user_id": user.id, "item_id": item_id}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        cart_item = await self.cartRepo.get_item_by_id(cart.id, item_id)
        if not cart_item:
            logger.warning("Update cart item failed: item not found", extra={"extra_fields": {"cart_id": cart.id, "item_id": item_id}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        if payload.quantity == 0:
            await self.cartRepo.delete_item(cart_item)
            logger.info("Cart item deleted due to zero quantity", extra={"extra_fields": {"cart_id": cart.id, "item_id": item_id}})
        else:
            product = await self.prodRepo.get_product(payload.product_id)
            if not product:
                logger.warning("Update cart item failed: product not found", extra={"extra_fields": {"cart_id": cart.id, "product_id": payload.product_id}})
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

            cart_item.product_id = payload.product_id
            cart_item.quantity = payload.quantity
            cart_item.price = payload.price
            logger.info(
                "Cart item updated",
                extra={"extra_fields": {
                    "cart_id": cart.id, 
                    "item_id": item_id, 
                    "product_id": cart_item.product_id, 
                    "quantity": cart_item.quantity, 
                    "price": cart_item.price
                }}
            )

        items = await self.cartRepo.get_items(cart.id)
        await self.update_cart_totals(cart, items)
        await self.cartRepo.commit()
        return await self._build_cart_out(cart, items)

    async def delete_cart_item(self, user, item_id: int) -> CartOut:
        cart = await self.cartRepo.get_cart_with_items(user.id)
        if not cart:
            logger.warning("Delete cart item failed: cart not found", extra={"extra_fields": {"user_id": user.id, "item_id": item_id}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        cart_item = await self.cartRepo.get_item_by_id(cart.id, item_id)
        if not cart_item:
            logger.warning("Delete cart item failed: item not found", extra={"extra_fields": {"cart_id": cart.id, "item_id": item_id}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        await self.cartRepo.delete_item(cart_item)
        logger.info("Cart item deleted", extra={"extra_fields": {"cart_id": cart.id, "item_id": item_id}})

        items = await self.cartRepo.get_items(cart.id)
        await self.update_cart_totals(cart, items)
        return await self._build_cart_out(cart, items)