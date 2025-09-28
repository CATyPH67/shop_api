from fastapi import HTTPException, status
from app.repositories.product_repository import ProductRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.category_repository import CategoryRepository
from app.pydantic_models import PaginatedProducts, PaginationMeta, ProductIn, ProductOut
from app.config.logging_config import logger
from fastapi_cache.decorator import cache
from app.config.cache_config import key_builder

class ProductService:
    def __init__(self, prodRepo: ProductRepository, sizeRepo: SizeRepository, categRepo: CategoryRepository):
        self.prodRepo = prodRepo
        self.sizeRepo = sizeRepo
        self.categRepo = categRepo

    async def create_product(self, product_data: ProductIn) -> ProductOut:
        logger.info("Attempting to create product", extra={"extra_fields": product_data.dict()})

        size = await self.sizeRepo.get_size_by_id(product_data.size_id)
        if not size:
            logger.exception("Size not found", extra={"extra_fields": {"size_id": product_data.size_id}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")

        categories = await self.categRepo.get_categories_by_ids(product_data.category_ids)
        if len(categories) != len(product_data.category_ids):
            missing = set(product_data.category_ids) - {c.id for c in categories}
            logger.exception("Categories not found", extra={"extra_fields": {"missing_category_ids": missing}})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

        try:
            product_full = await self.prodRepo.create_product(
                name=product_data.name,
                description=product_data.description,
                image=product_data.image,
                price=product_data.price,
                size=size,
                categories=categories
            )
        except Exception:
            logger.exception("Error while creating product", extra={"extra_fields": product_data.dict()})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create product")

        logger.info("Product created successfully", extra={"extra_fields": {"id": product_full.id}})

        return ProductOut(
            id=product_full.id,
            name=product_full.name,
            description=product_full.description,
            image=product_full.image,
            price=product_full.price,
            size=product_full.size.name if product_full.size else None,
            categories=[c.name for c in product_full.categories]
        )

    @cache(expire=60, namespace="get_products", key_builder=key_builder)
    async def get_products(
        self,
        category_id: int,
        min_price: float | None,
        max_price: float | None,
        sort: str | None,
        limit: int,
        offset: int,
    ) -> PaginatedProducts:
        try:
            prods, has_next = await self.prodRepo.get_filtered(
                category_id, min_price, max_price, sort, limit, offset
            )
        except Exception:
            logger.exception("Error fetching products")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")

        items = []
        for p in prods:
            items.append(
                ProductOut(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    image=p.image,
                    price=p.price,
                    size=p.size.name if p.size else None,
                    categories=[c.name for c in p.categories],
                )
            )

        return PaginatedProducts(
            items=items,
            meta=PaginationMeta(limit=limit, offset=offset, has_next=has_next),
        )

    @cache(expire=60, namespace="get_product", key_builder=key_builder)
    async def get_product(self, product_id: int) -> ProductOut:
        logger.info(
            "Fetching product by ID",
            extra={"extra_fields": {"product_id": product_id}}
        )

        p = await self.prodRepo.get_product_joined(product_id)
        if not p:
            logger.warning(
                "Product not found",
                extra={"extra_fields": {"product_id": product_id}}
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        cat_names = [c.name for c in p.categories]
        size_name = p.size.name if p.size else None

        logger.info(
            "Product fetched successfully",
            extra={"extra_fields": {"product_id": product_id}}
        )

        return ProductOut(
            id=p.id,
            name=p.name,
            description=p.description,
            image=p.image,
            price=p.price,
            size=size_name,
            categories=cat_names,
        )