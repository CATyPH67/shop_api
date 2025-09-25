from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Category
from app.db.database import get_session
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="", tags=["categories"])

class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    subcategories: List["CategoryOut"] = []

    class Config:
        orm_mode = True

@router.get("/categories", response_model=List[CategoryOut])
async def get_categories(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Category))
    cats = res.scalars().all()

    id_map = {c.id: {"id": c.id, "name": c.name, "parent_id": c.parent_id, "subcategories": []} for c in cats}
    roots = []
    for c in cats:
        node = id_map[c.id]
        if c.parent_id:
            id_map[c.parent_id]["subcategories"].append(node)
        else:
            roots.append(node)
    return roots
