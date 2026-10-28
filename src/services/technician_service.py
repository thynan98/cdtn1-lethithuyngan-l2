"""Tầng 3 - nghiệp vụ kỹ thuật viên (thực thể thứ hai có đủ thêm, xem, sửa, ngừng hoạt động).

QT-13: không xóa cứng. "Ngừng hoạt động" chỉ đặt is_active = False; kỹ thuật viên
đó biến mất khỏi danh sách chọn nhưng lịch sử các phiếu cũ vẫn giữ nguyên.
"""
from src.errors import AppError
from src.validators.technician_validator import validate_create_technician, validate_update_technician


def _public(t):
    return {"technician_id": t["technician_id"], "technician_code": t["technician_code"],
            "full_name": t["full_name"], "is_active": t["is_active"]}


class TechnicianService:
    def __init__(self, technicians):
        self.technicians = technicians

    def list_technicians(self, include_inactive=False):
        return {"items": [_public(t) for t in self.technicians.list(include_inactive)]}

    def create(self, body):
        code, name = validate_create_technician(body)
        if self.technicians.find_by_code(code):
            raise AppError("DUPLICATE_CODE", "Mã kỹ thuật viên đã tồn tại",
                           {"technician_code": "Mã này đã được dùng"})
        return _public(self.technicians.insert(code, name))

    def update(self, technician_id, body):
        changes = validate_update_technician(body)
        self._get_or_404(technician_id)
        self.technicians.update(technician_id, changes)
        return _public(self.technicians.get(technician_id))

    def deactivate(self, technician_id):
        """Xóa mềm. Gọi lại nhiều lần vẫn cho cùng kết quả."""
        self._get_or_404(technician_id)
        self.technicians.update(technician_id, {"is_active": False})
        return _public(self.technicians.get(technician_id))

    def _get_or_404(self, technician_id):
        technician = self.technicians.get(technician_id)
        if technician is None:
            raise AppError("NOT_FOUND", "Không tìm thấy kỹ thuật viên")
        return technician
