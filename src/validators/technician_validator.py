"""Tầng 1 - kiểm tra định dạng dữ liệu kỹ thuật viên."""
import re

from src.errors import AppError

CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,20}$")


def _check_name(name, missing, invalid):
    if not name:
        missing["full_name"] = "Họ tên không được để trống"
    elif len(name) > 120:
        invalid["full_name"] = "Họ tên tối đa 120 ký tự"


def validate_create_technician(body):
    """Body của POST /api/technicians. Trả về (technician_code, full_name)."""
    body = body or {}
    missing, invalid = {}, {}

    code = str(body.get("technician_code") or "").strip().upper()
    if not code:
        missing["technician_code"] = "Mã kỹ thuật viên không được để trống"
    elif not CODE_PATTERN.match(code):
        invalid["technician_code"] = "Mã chỉ gồm chữ, số, gạch ngang hoặc gạch dưới, tối đa 20 ký tự"

    name = str(body.get("full_name") or "").strip()
    _check_name(name, missing, invalid)

    if missing:
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ", {**missing, **invalid})
    if invalid:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ", invalid)
    return code, name


def validate_update_technician(body):
    """Body của PATCH /api/technicians/{id}. Trả về dict các trường được phép đổi.

    Chỉ cho đổi full_name và is_active; mã kỹ thuật viên không đổi sau khi tạo.
    """
    body = body or {}
    changes, missing, invalid = {}, {}, {}

    if "full_name" in body:
        name = str(body.get("full_name") or "").strip()
        _check_name(name, missing, invalid)
        changes["full_name"] = name
    if "is_active" in body:
        if not isinstance(body["is_active"], bool):
            invalid["is_active"] = "is_active phải là true hoặc false"
        else:
            changes["is_active"] = body["is_active"]

    if not changes:
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ",
                       {"body": "Cần ít nhất một trường: full_name hoặc is_active"})
    if missing:
        raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ", {**missing, **invalid})
    if invalid:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ", invalid)
    return changes
