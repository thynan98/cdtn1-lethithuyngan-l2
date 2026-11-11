"""Hồi quy cho BUG-006: id quá lớn (quá 8 byte) phải ra "không tìm thấy", không được làm sập thành lỗi 500."""
from types import SimpleNamespace

import bson

from src.repositories.category_repository import CategoryRepository
from src.repositories.technician_repository import TechnicianRepository
from src.repositories.ticket_repository import TicketRepository

ID_QUA_LON = 99999999999999999999      # lớn hơn 9223372036854775807 (số nguyên 8 byte lớn nhất)


class KhoGiaLap:
    """Mô phỏng collection MongoDB: mã hóa câu truy vấn đúng như pymongo, nên id quá lớn sẽ ném OverflowError."""

    def find_one(self, query, projection=None):
        bson.encode(query)
        return {"tim_thay": True}          # nếu tới được đây thì trả về một bản ghi


def kho():
    c = KhoGiaLap()
    return SimpleNamespace(ticket=c, technician=c, issue_category=c)


def test_bug006_phieu_id_qua_lon_khong_tim_thay():
    assert TicketRepository(kho()).get(ID_QUA_LON) is None


def test_bug006_ky_thuat_vien_id_qua_lon_khong_tim_thay():
    assert TechnicianRepository(kho()).get(ID_QUA_LON) is None


def test_bug006_loai_loi_id_qua_lon_khong_tim_thay():
    assert CategoryRepository(kho()).get(ID_QUA_LON) is None


def test_bug006_id_hop_le_van_duoc_tra_cuu():
    assert TicketRepository(kho()).get(1) == {"tim_thay": True}     # id bình thường không bị chặn nhầm