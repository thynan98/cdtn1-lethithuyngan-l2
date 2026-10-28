"""Tầng 1 - cổng HTTP của phiếu bảo hành. KHÔNG chứa quy tắc nghiệp vụ.

Việc của route: nhận yêu cầu → kiểm quyền → gọi service → trả kết quả.
Lỗi nghiệp vụ (AppError) được src/main.py đổi thành mã HTTP và thân lỗi chuẩn.
"""
from fastapi import APIRouter, Body, Depends

from src.dependencies import get_ticket_service, require_permission
from src.services.ticket_service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", status_code=201)
def create_ticket(body: dict = Body(...), service: TicketService = Depends(get_ticket_service),
                  user=Depends(require_permission("ticket:create"))):
    return service.create_ticket(body)


@router.get("")
def list_tickets(status: str | None = None, overdue: bool = False, page: int = 1, size: int = 20,
                 service: TicketService = Depends(get_ticket_service),
                 user=Depends(require_permission("ticket:view"))):
    return service.list_tickets(status=status, overdue=overdue, page=page, size=size)


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, service: TicketService = Depends(get_ticket_service),
               user=Depends(require_permission("ticket:view"))):
    return service.get_ticket(ticket_id)


@router.patch("/{ticket_id}/category")
def set_category(ticket_id: int, body: dict = Body(...),
                 service: TicketService = Depends(get_ticket_service),
                 user=Depends(require_permission("ticket:classify"))):
    return service.set_category(ticket_id, body)


@router.patch("/{ticket_id}/technician")
def assign_technician(ticket_id: int, body: dict = Body(...),
                      service: TicketService = Depends(get_ticket_service),
                      user=Depends(require_permission("ticket:assign"))):
    return service.assign_technician(ticket_id, body)


@router.patch("/{ticket_id}/status")
def change_status(ticket_id: int, body: dict = Body(...),
                  service: TicketService = Depends(get_ticket_service),
                  user=Depends(require_permission("ticket:status"))):
    return service.change_status(ticket_id, body)


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, service: TicketService = Depends(get_ticket_service),
                  user=Depends(require_permission("ticket:delete"))):
    return service.delete_ticket(ticket_id)
