from app.repositories.category_repository import CategoryRepository
from app.pydantic_models import CategoryOut, PaginatedCategories, PaginationMeta
from app.config.logging_config import logger
from fastapi_cache.decorator import cache
from app.utils.cache_utils import key_builder


class CategoryService:
    def __init__(self, cartRepo: CategoryRepository):
        self.cartRepo = cartRepo

    @cache(expire=60, namespace="get_categories", key_builder=key_builder)
    async def get_categories(self, limit: int, offset: int) -> PaginatedCategories:
        logger.info("Fetching categories", extra={"extra_fields": {"limit": limit, "offset": offset}})
        try:
            categories, has_next = await self.cartRepo.get_all(limit, offset)

            items = [
                CategoryOut(id=c.id, name=c.name, parent_id=c.parent_id)
                for c in categories
            ]

            return PaginatedCategories(
                items=items,
                meta=PaginationMeta(limit=limit, offset=offset, has_next=has_next),
            )

        except Exception:
            logger.exception("Failed to fetch categories")
            raise