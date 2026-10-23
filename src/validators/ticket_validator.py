"""Tầng 1 - kiểm tra định dạng dữ liệu vào. Chưa tra CSDL."""
import re

from src.errors import AppError

PRIORITIES = ("CAO", "TRUNG_BINH", "THAP")
PHONE_PATTERN = re.compile(r"^0[0-9]{9}$")


def normalize_phone(raw):
    """QT-02: chuẩn hóa số điện thoại về 10 chữ số bắt đầu bằng 0."""
    phone = re.sub(r"[\s.\-]", "", str(raw or ""))
    if phone.startswith("+84"):
        phone = "0" + phone[3:]
    elif phone.startswith("84") and len(phone) == 11:
        phone = "0" + phone[2:]
    return phone


def validate_create_ticket(body):
    """Kiểm tra body của POST /api/tickets, trả về dữ liệu đã chuẩn hóa.

    Thiếu trường    -> AppError REQUIRED_FIELD_MISSING
    Sai định dạng   -> AppError INVALID_FORMAT
    Gom TẤT CẢ lỗi rồi báo một lần để người dùng sửa một lượt.
    """
    body = body or {}
    missing, invalid = {}, {}

    name = str(body.get("customer_name") or "").strip()
    if not name:
        missing["customer_name"] = "Tên khách hàng không được để trống"
    elif len(name) > 120:
        invalid["customer_name"] = "Tên khách hàng tối đa 120 ký tự"

    phone = normalize_phone(body.get("customer_phone"))
    if not phone:
        missing["customer_phone"] = "Trường bắt buộc, không được để trống"
    elif not PHONE_PATTERN.match(phone):
        invalid["customer_phone"] = "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0"

    desc = str(body.get("issue_desc") or "").strip()
    if not desc:
        missing["issue_desc"] = "Trường bắt buộc, không được để trống"
    elif not 10 <= len(desc) <= 2000:
        invalid["issue_desc"] = "Mô tả lỗi phải có từ 10 đến 2000 ký tự"

    priority = body.get("priority") or "TRUNG_BINH"
    if priority not in PRIORITIES:
        invalid["priority"] = "Mức ưu tiên không hợp lệ"

    if missing:
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ", {**missing, **invalid})
    if invalid:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ", invalid)
    return {"customer_name": name, "customer_phone": phone,
            "issue_desc": desc, "priority": priority}
