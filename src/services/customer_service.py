"""Tầng 3 - nghiệp vụ tra cứu khách hàng (US7)."""
from src.errors import AppError
from src.timeutil import iso_vn
from src.validators.ticket_validator import PHONE_PATTERN, normalize_phone


class CustomerService:
    def __init__(self, customers, tickets):
        self.customers = customers
        self.tickets = tickets

    def find_by_phone(self, raw_phone):
        if not str(raw_phone or "").strip():
            raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ",
                           {"phone": "Trường bắt buộc, không được để trống"})
        phone = normalize_phone(raw_phone)            # QT-02: cùng quy tắc chuẩn hóa như khi tạo phiếu
        if not PHONE_PATTERN.match(phone):
            raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                           {"phone": "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0"})
        customer = self.customers.find_by_phone(phone)
        if customer is None:
            raise AppError("NOT_FOUND", "Không tìm thấy khách hàng")
        recent = self.tickets.list_by_customer(customer["customer_id"], limit=10)
        return {
            "customer_id": customer["customer_id"], "full_name": customer["full_name"],
            "phone": customer["phone"],
            "tickets": [{"ticket_id": t["ticket_id"], "ticket_code": t["ticket_code"],
                         "status": t["status"], "received_at": iso_vn(t["received_at"])}
                        for t in recent],
        }
