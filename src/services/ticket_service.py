"""Tầng nghiệp vụ của phiếu bảo hành.

Quy tắc ở đây KHÔNG biết gì về HTTP: không request, không mã trạng thái.
Phần có kết nối repository sẽ thêm vào lớp TicketService ở bước sau.
"""
from datetime import timedelta

from src.errors import AppError

SLA_WORKING_DAYS = {"CAO": 1, "TRUNG_BINH": 3, "THAP": 5}   # = 24 / 72 / 120 giờ
NEXT_STATUS = {"MOI": "DANG_XU_LY", "DANG_XU_LY": "HOAN_TAT"}
ALL_STATUSES = ("MOI", "DANG_XU_LY", "HOAN_TAT")
SUNDAY = 6   # datetime.weekday(): thứ Hai = 0 ... Chủ nhật = 6


def calculate_due_date(received_at, priority):
    """QT-04: hạn cam kết = lúc tiếp nhận + 24/72/120 giờ, không tính Chủ nhật."""
    if priority not in SLA_WORKING_DAYS:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"priority": "Mức ưu tiên không hợp lệ"})
    days_left = SLA_WORKING_DAYS[priority]
    due = received_at
    while days_left > 0:
        due += timedelta(days=1)
        if due.weekday() != SUNDAY:      # Chủ nhật không được đếm
            days_left -= 1
    return due


def check_status_transition(current, new):
    """QT-06: chỉ cho chuyển một chiều MOI -> DANG_XU_LY -> HOAN_TAT."""
    if new not in ALL_STATUSES:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"status": "Trạng thái không hợp lệ"})
    if NEXT_STATUS.get(current) != new:
        raise AppError("INVALID_TRANSITION", "Sai thứ tự chuyển trạng thái")
