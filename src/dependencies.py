"""Nối các tầng với nhau (tiêm phụ thuộc) và kiểm tra đăng nhập cho FastAPI.

Route chỉ gọi các hàm get_*_service ở đây; khi kiểm thử, các hàm này được thay bằng
bản dùng kho dữ liệu giả (app.dependency_overrides) nên không cần MongoDB.
"""
from fastapi import Depends, Header

from src import config
from src.database import get_db
from src.errors import AppError
from src.repositories.category_repository import CategoryRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.log_repository import LogRepository
from src.repositories.technician_repository import TechnicianRepository
from src.repositories.ticket_repository import TicketRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.category_service import CategoryService
from src.services.customer_service import CustomerService
from src.services.technician_service import TechnicianService
from src.services.ticket_service import TicketService


def get_ticket_service():
    db = get_db()
    return TicketService(TicketRepository(db), CustomerRepository(db), TechnicianRepository(db),
                         CategoryRepository(db), LogRepository(db))


def get_technician_service():
    return TechnicianService(TechnicianRepository(get_db()))


def get_customer_service():
    db = get_db()
    return CustomerService(CustomerRepository(db), TicketRepository(db))


def get_category_service():
    return CategoryService(CategoryRepository(get_db()))


def get_auth_service():
    return AuthService(UserRepository(get_db()), config.JWT_SECRET, config.JWT_EXPIRE_MINUTES)


def current_user(authorization: str | None = Header(default=None),
                 auth: AuthService = Depends(get_auth_service)):
    """Đọc header "Authorization: Bearer <token>"; thiếu hoặc sai thì lỗi 401."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError("UNAUTHORIZED", "Vui lòng đăng nhập")
    return auth.verify_token(authorization[7:].strip())


def require_permission(permission):
    """Tạo một phụ thuộc: phải đăng nhập VÀ vai trò có quyền này, nếu không lỗi 401/403."""
    def check(user=Depends(current_user)):
        AuthService.require(user["role"], permission)
        return user
    return check
