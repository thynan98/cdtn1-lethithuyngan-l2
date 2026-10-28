import pytest

from src.errors import AppError


def test_create_uppercases_code(technician_service):
    created = technician_service.create({"technician_code": "ktv009", "full_name": "Lê Văn Chín"})
    assert created["technician_code"] == "KTV009" and created["is_active"] is True


def test_duplicate_code_is_rejected(technician_service):
    with pytest.raises(AppError) as err:
        technician_service.create({"technician_code": "KTV001", "full_name": "Người trùng mã"})
    assert err.value.code == "DUPLICATE_CODE"


def test_missing_name_is_rejected(technician_service):
    with pytest.raises(AppError) as err:
        technician_service.create({"technician_code": "KTV010"})
    assert err.value.code == "REQUIRED_FIELD_MISSING"
    assert "full_name" in err.value.fields


def test_deactivate_is_soft_and_repeatable(technician_service):
    technician_service.deactivate(1)
    again = technician_service.deactivate(1)
    assert again["is_active"] is False
    codes = [t["technician_code"] for t in technician_service.list_technicians()["items"]]
    assert "KTV001" not in codes                                       # biến khỏi danh sách chọn
    all_codes = [t["technician_code"] for t in technician_service.list_technicians(True)["items"]]
    assert "KTV001" in all_codes                                       # nhưng dữ liệu còn


def test_update_unknown_technician(technician_service):
    with pytest.raises(AppError) as err:
        technician_service.update(99, {"full_name": "Ai đó"})
    assert err.value.code == "NOT_FOUND"
