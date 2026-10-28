"""Tầng 1 - cổng HTTP tra cứu khách hàng (US7)."""
from fastapi import APIRouter, Depends

from src.dependencies import get_customer_service, require_permission
from src.services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def find_customer(phone: str = "", service: CustomerService = Depends(get_customer_service),
                  user=Depends(require_permission("customer:view"))):
    return service.find_by_phone(phone)
