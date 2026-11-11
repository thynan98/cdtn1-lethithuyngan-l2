"""Hồi quy cho BUG-005: ứng dụng phải dừng khi thiếu khóa ký token hoặc khóa quá ngắn."""
import pytest

from src import config


def test_bug005_thieu_khoa_thi_khong_khoi_dong():
    with pytest.raises(RuntimeError):
        config.check_jwt_secret("")


def test_bug005_khoa_qua_ngan_bi_tu_choi():
    with pytest.raises(RuntimeError):
        config.check_jwt_secret("a" * 31)


def test_bug005_khoa_du_32_ky_tu_duoc_chap_nhan():
    config.check_jwt_secret("a" * 32)       # không ném lỗi