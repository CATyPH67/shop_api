import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import async_session_maker, engine, Base
from app.db.models import Category, Size, Product, User
from app.utils.security import get_password_hash  # ✅ заменили путь


async def seed():
    async with engine.begin() as conn:
        # Создадим таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:  # type: AsyncSession
        # Проверим, есть ли данные
        result = await session.execute(select(Category))
        if result.scalars().first():
            print("⚠️ Данные уже есть, пропускаем заполнение.")
            return

        # --- Пользователь с ролью админ ---
        hashed_password = get_password_hash("admin")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hashed_password,
            role="admin",
        )
        session.add(admin_user)

        # --- Категории ---
        furs = Category(name="Меха", parent_id=None)
        coats = Category(name="Шубы", parent_id=None)

        furs_children = [
            Category(name="Норка", parent=furs),
            Category(name="Лиса", parent=furs),
            Category(name="Соболь", parent=furs),
        ]

        coats_children = [
            Category(name="Длинные", parent=coats),
            Category(name="Короткие", parent=coats),
            Category(name="С капюшоном", parent=coats),
        ]

        session.add_all([furs, coats] + furs_children + coats_children)

        # --- Размеры ---
        sizes = [Size(name=n) for n in ["XS", "S", "M", "L", "XL", "XXL"]]
        session.add_all(sizes)

        await session.flush()  # чтобы появились id

        # --- Продукты ---
        products = []
        for i in range(1, 101):
            parent = random.choice([furs, coats])
            if parent == furs:
                child = random.choice(furs_children)
            else:
                child = random.choice(coats_children)

            product = Product(
                name=f"Товар {i}",
                description=f"Описание товара {i}",
                image=f"https://example.com/image_{i}.jpg",
                price=random.randint(5000, 50000),
                size=random.choice(sizes),
            )

            # Добавляем категории: родительская и дочерняя
            product.categories.append(parent)
            product.categories.append(child)

            products.append(product)

        session.add_all(products)
        await session.commit()

        print("✅ База успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    asyncio.run(seed())