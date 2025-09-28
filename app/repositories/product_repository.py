from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.models import Product, Category, Size, product_category
from sqlalchemy.orm import selectinload


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_size_by_id(self, size_id: int) -> Size | None:
        result = await self.session.execute(select(Size).where(Size.id == size_id))
        return result.scalar_one_or_none()

    async def get_categories_by_ids(self, category_ids: list[int]) -> list[Category]:
        result = await self.session.execute(select(Category).where(Category.id.in_(category_ids)))
        return result.scalars().all()

    async def create_product(
        self,
        name: str,
        description: str,
        image: str,
        price: float,
        size: Size,
        categories: list[Category],
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            image=image,
            price=price,
            size=size,
            categories=categories
        )
        self.session.add(product)
        await self.session.commit()

        # Подгружаем связи сразу, чтобы не было lazy-load
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.size), selectinload(Product.categories))
            .where(Product.id == product.id)
        )
        return result.scalar_one()

    async def get_filtered(
        self,
        category_id: int,
        min_price: float | None,
        max_price: float | None,
        sort: str | None,
    ) -> list[Product]:
        q = (
            select(Product)
            .join(product_category, Product.id == product_category.c.product_id)
            .join(Category, Category.id == product_category.c.category_id)
            .where(Category.id == category_id)
            .options(joinedload(Product.categories), joinedload(Product.size))
        )

        if min_price is not None:
            q = q.where(Product.price >= min_price)
        if max_price is not None:
            q = q.where(Product.price <= max_price)
        if sort == "price_asc":
            q = q.order_by(Product.price.asc())
        elif sort == "price_desc":
            q = q.order_by(Product.price.desc())

        res = await self.session.execute(q)
        return res.scalars().unique().all()

    async def get_by_id(self, product_id: int) -> Product | None:
        res = await self.session.execute(
            select(Product)
            .options(joinedload(Product.categories), joinedload(Product.size))
            .where(Product.id == product_id)
        )
        return res.unique().scalar_one_or_none()
