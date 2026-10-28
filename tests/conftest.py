import pytest

from src.services.auth_service import AuthService
from src.services.technician_service import TechnicianService
from src.services.ticket_service import TicketService
from tests import fakes


@pytest.fixture
def repos():
    return {
        "tickets": fakes.FakeTickets(), "customers": fakes.FakeCustomers(),
        "technicians": fakes.FakeTechnicians(fakes.TECHNICIANS),
        "categories": fakes.FakeCategories(fakes.CATEGORIES), "logs": fakes.FakeLogs(),
    }


@pytest.fixture
def ticket_service(repos):
    return TicketService(repos["tickets"], repos["customers"], repos["technicians"],
                         repos["categories"], repos["logs"], clock=lambda: fakes.at(5))


@pytest.fixture
def technician_service(repos):
    return TechnicianService(repos["technicians"])


@pytest.fixture
def users():
    return fakes.FakeUsers([
        {"user_id": 1, "username": "nv", "full_name": "Nhân Viên", "role": "NHAN_VIEN", "is_active": True,
         "password_hash": AuthService.hash_password("MatKhau@1", iterations=1000)},
        {"user_id": 2, "username": "ql", "full_name": "Quản Lý", "role": "QUAN_LY", "is_active": True,
         "password_hash": AuthService.hash_password("MatKhau@2", iterations=1000)},
    ])


@pytest.fixture
def auth(users):
    # Dùng đồng hồ thật: JWT tự kiểm hạn theo giờ thật, đồng hồ giả sẽ làm token hết hạn ngay
    return AuthService(users, "khoa-chi-dung-de-kiem-thu-0123456789", 480)


NEW_TICKET = {"customer_name": "Nguyễn Thị Lan", "customer_phone": "0901000001",
              "issue_desc": "Màn hình bị sọc ngang", "priority": "TRUNG_BINH"}
