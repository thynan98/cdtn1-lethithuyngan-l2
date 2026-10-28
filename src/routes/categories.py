"""Tầng 1 - cổng HTTP danh sách loại lỗi (US2)."""
from fastapi import APIRouter, Depends

from src.dependencies import get_category_repository, require_permission

router = APIRouter(prefix="/api/issue-categories", tags=["issue-categories"])


@router.get("")
def list_categories(categories=Depends(get_category_repository),
                    user=Depends(require_permission("ticket:view"))):
    return {"items": [{"category_id": c["category_id"], "category_code": c["category_code"],
                       "category_name": c["category_name"]} for c in categories.list_active()]}
