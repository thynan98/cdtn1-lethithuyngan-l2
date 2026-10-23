from datetime import datetime, timedelta, timezone

import pytest

from src.errors import AppError
from src.services.ticket_service import calculate_due_date, check_status_transition
from src.validators.ticket_validator import normalize_phone, validate_create_ticket

VN = timezone(timedelta(hours=7))


def at(day, hour=14, minute=30):
    """Tạo thời điểm trong tháng 10/2026 (múi giờ Việt Nam)."""
    return datetime(2026, 10, day, hour, minute, tzinfo=VN)


# ---- Loại 1: luồng đúng --------------------------------------------------
def test_tc01_happy_due_date_medium_priority():
    # Thứ Hai 05/10 + 3 ngày làm việc = thứ Năm 08/10 (khớp ví dụ trong api-contract)
    assert calculate_due_date(at(5), "TRUNG_BINH") == at(8)


def test_tc04_happy_status_moves_one_way():
    check_status_transition("MOI", "DANG_XU_LY")        # không ném lỗi
    check_status_transition("DANG_XU_LY", "HOAN_TAT")   # không ném lỗi


def test_tc07_happy_phone_normalized_to_10_digits():
    assert normalize_phone("+84 912.345 678") == "0912345678"
    assert normalize_phone("84912345678") == "0912345678"


# ---- Loại 2: giá trị biên -----------------------------------------------
def test_tc02_boundary_saturday_high_priority_skips_sunday():
    # Thứ Bảy 10/10 + 1 ngày làm việc: Chủ nhật 11/10 bị bỏ qua -> thứ Hai 12/10
    assert calculate_due_date(at(10), "CAO") == at(12)


def test_tc03_boundary_low_priority_crosses_sunday():
    # Thứ Ba 06/10 + 5 ngày làm việc: T4, T5, T6, T7, (bỏ CN), T2 -> 12/10
    assert calculate_due_date(at(6), "THAP") == at(12)


def test_tc08_boundary_description_exactly_10_chars_is_accepted():
    data = validate_create_ticket({"customer_name": "An", "customer_phone": "0912345678",
                                   "issue_desc": "1234567890"})
    assert data["priority"] == "TRUNG_BINH"             # mặc định theo hợp đồng


# ---- Loại 3: dữ liệu sai ------------------------------------------------
def test_tc05_invalid_status_cannot_skip_step():
    with pytest.raises(AppError) as err:
        check_status_transition("MOI", "HOAN_TAT")
    assert err.value.code == "INVALID_TRANSITION"


def test_tc06_invalid_missing_phone_returns_field_name():
    with pytest.raises(AppError) as err:
        validate_create_ticket({"customer_name": "An", "issue_desc": "Máy sạc không vào"})
    assert err.value.code == "REQUIRED_FIELD_MISSING"
    assert "customer_phone" in err.value.fields