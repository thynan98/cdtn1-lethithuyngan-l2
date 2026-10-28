"""Tầng 1 - kiểm tra định dạng dữ liệu vào. Chưa tra CSDL."""
import re

from src.errors import AppError

PRIORITIES = ("CAO", "TRUNG_BINH", "THAP")
STATUSES = ("MOI", "DANG_XU_LY", "HOAN_TAT")
PHONE_PATTERN = re.compile(r"^0[0-9]{9}$")


def normalize_phone(raw):
    """QT-02: chuẩn hóa số điện thoại về 10 chữ số bắt đầu bằng 0."""
    phone = re.sub(r"[\s.\-]", "", str(raw or ""))
    if phone.startswith("+84"):
        phone = "0" + phone[3:]
    elif phone.startswith("84") and len(phone) == 11:
        phone = "0" + phone[2:]
    return phone


def is_positive_int(value):
    """Số nguyên dương (True/False của Python cũng là int nên phải loại ra)."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


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


def validate_status_body(body):
    """Body của PATCH /api/tickets/{id}/status. Trả về mã trạng thái mới."""
    value = (body or {}).get("status")
    if value is None or value == "":
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ",
                       {"status": "Trường bắt buộc, không được để trống"})
    if value not in STATUSES:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"status": "Trạng thái không hợp lệ"})
    return value


def validate_assign_body(body):
    """Body của PATCH /api/tickets/{id}/technician. Trả về technician_id."""
    value = (body or {}).get("technician_id")
    if value is None or value == "":
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ",
                       {"technician_id": "Trường bắt buộc, không được để trống"})
    if not is_positive_int(value):
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"technician_id": "Mã kỹ thuật viên phải là số nguyên dương"})
    return value


def validate_category_body(body):
    """Body của PATCH /api/tickets/{id}/category. Trả về category_id."""
    value = (body or {}).get("category_id")
    if value is None or value == "":
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ",
                       {"category_id": "Trường bắt buộc, không được để trống"})
    if not is_positive_int(value):
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"category_id": "Mã loại lỗi phải là số nguyên dương"})
    return value


def validate_list_params(status, page, size):
    """Tham số của GET /api/tickets: status hợp lệ, page >= 1, 1 <= size <= 100."""
    invalid = {}
    if status is not None and status not in STATUSES:
        invalid["status"] = "Trạng thái không hợp lệ"
    if not is_positive_int(page):
        invalid["page"] = "page phải là số nguyên từ 1 trở lên"
    if not (is_positive_int(size) and size <= 100):
        invalid["size"] = "size phải là số nguyên từ 1 đến 100"
    if invalid:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ", invalid)
