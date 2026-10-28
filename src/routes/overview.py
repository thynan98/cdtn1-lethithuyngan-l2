"""Tầng 2 (lớp routes) - cổng HTTP màn Tổng quan (TD-08): số phiếu theo trạng thái và phiếu cần chú ý."""
from fastapi import APIRouter, Depends

from src.dependencies import get_ticket_service, require_permission
from src.services.ticket_service import TicketService

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("")
def overview(service: TicketService = Depends(get_ticket_service),
             user=Depends(require_permission("overview:view"))):
    return service.overview()
