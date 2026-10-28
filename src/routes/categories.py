"""Tầng 1 - cổng HTTP danh sách loại lỗi (US2)."""
from fastapi import APIRouter, Depends

from src.dependencies import get_category_service, require_permission
from src.services.category_service import CategoryService

router = APIRouter(prefix="/api/issue-categories", tags=["issue-categories"])


@router.get("")
def list_categories(service: CategoryService = Depends(get_category_service),
                    user=Depends(require_permission("ticket:view"))):
    return service.list_categories()
