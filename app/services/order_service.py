from fastapi import HTTPException, status
from app.repositories.order_repository import OrderRepository
from app.pydantic_models import OrderOut, OrderItemOut
from app.services.email_service import send_email
from app.config.logging_config import logger


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def create_order(self, user, background_tasks) -> OrderOut:
        logger.info("Creating order", extra={"extra_fields": {"user_id": str(user.id)}})
        
        cart = await self.repo.get_cart_with_items(user.id)
        if not cart or not cart.items:
            logger.warning("Cart is empty", extra={"extra_fields": {"user_id": str(user.id)}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        order = await self.repo.create_order(user.id, cart.total_price, cart.total_quantity)
        items = await self.repo.get_cart_items(cart.id)

        logger.info(
            "Order created in DB",
            extra={"extra_fields": {"order_id": str(order.id), "total_price": order.total_price}}
        )

        order_items = []
        for ci in items:
            oi = await self.repo.add_order_item(order.id, ci.product_id, ci.quantity, ci.price)
            order_items.append(oi)

        await self.repo.clear_cart(cart, items)
        await self.repo.commit()

        logger.info(
            "Cart cleared after order creation",
            extra={"extra_fields": {"user_id": str(user.id), "order_id": str(order.id)}}
        )

        # Отправка письма
        try:
            background_tasks.add_task(
                send_email,
                user.email,
                "Ваш заказ принят",
                f"""
                <h2>Спасибо за заказ!</h2>
                <p>Номер заказа: {order.id}</p>
                <p>Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                <p>Сумма: {order.total_price} руб.</p>
                """
            )
            logger.info(
                "Email task added to background",
                extra={"extra_fields": {"user_email": str(user.email), "order_id": str(order.id)}}
            )
        except Exception as e:
            logger.exception(
                "Failed to schedule email",
                extra={"extra_fields": {"user_email": str(user.email), "order_id": str(order.id)}}
            )
            raise e

        return OrderOut(
            id=order.id,
            total_price=order.total_price,
            total_quantity=order.total_quantity,
            created_at=order.created_at,
            items=[
                OrderItemOut(
                    id=oi.id,
                    product_id=oi.product_id,
                    quantity=oi.quantity,
                    price=oi.price,
                )
                for oi in order_items
            ],
        )