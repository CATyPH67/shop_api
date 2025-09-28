from app.repositories.category_repository import CategoryRepository
from app.pydantic_models import CategoryOut
from app.config.logging_config import logger


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def get_categories(self) -> list[CategoryOut]:
        logger.info("Fetching all categories")
        try:
            categories = await self.repo.get_all()
            logger.info(
                "Categories fetched successfully",
                extra={"extra_fields": {"count": len(categories)}}
            )

            id_map = {
                c.id: {"id": c.id, "name": c.name, "parent_id": c.parent_id, "subcategories": []}
                for c in categories
            }

            roots = []
            for c in categories:
                node = id_map[c.id]
                if c.parent_id:
                    id_map[c.parent_id]["subcategories"].append(node)
                else:
                    roots.append(node)

            logger.info(
                "Categories structured into tree",
                extra={"extra_fields": {"root_count": len(roots)}}
            )
            return roots

        except Exception as e:
            logger.exception("Failed to fetch categories")
            raise e