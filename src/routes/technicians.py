"""Tầng 2 (lớp routes) - cổng HTTP của kỹ thuật viên."""
from fastapi import APIRouter, Body, Depends

from src.dependencies import current_user, get_technician_service, require_permission
from src.services.auth_service import AuthService
from src.services.technician_service import TechnicianService

router = APIRouter(prefix="/api/technicians", tags=["technicians"])


@router.get("")
def list_technicians(include_inactive: bool = False,
                     service: TechnicianService = Depends(get_technician_service),
                     user=Depends(require_permission("technician:view"))):
    # Chỉ người có quyền quản lý mới được xem cả kỹ thuật viên đã ngừng hoạt động
    show_all = include_inactive and AuthService.can(user["role"], "technician:manage")
    return service.list_technicians(include_inactive=show_all)


@router.post("", status_code=201)
def create_technician(body: dict = Body(...),
                      service: TechnicianService = Depends(get_technician_service),
                      user=Depends(require_permission("technician:manage"))):
    return service.create(body)


@router.patch("/{technician_id}")
def update_technician(technician_id: int, body: dict = Body(...),
                      service: TechnicianService = Depends(get_technician_service),
                      user=Depends(require_permission("technician:manage"))):
    return service.update(technician_id, body)


@router.delete("/{technician_id}")
def deactivate_technician(technician_id: int,
                          service: TechnicianService = Depends(get_technician_service),
                          user=Depends(require_permission("technician:manage"))):
    return service.deactivate(technician_id)
