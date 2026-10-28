"""Hồi quy cho BUG-003: .gitignore phải chặn tệp .env thật (chứa chuỗi kết nối cơ sở dữ liệu)."""
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


def doc_dong(ten_tep):
    # splitlines() bỏ cả ký tự xuống dòng kiểu Windows (CRLF) lẫn Linux (LF)
    return [d.strip() for d in (GOC / ten_tep).read_text(encoding="utf-8").splitlines()]


def test_bug003_gitignore_chan_tep_env():
    dong = doc_dong(".gitignore")
    assert ".env" in dong, "Thiếu dòng '.env' trong .gitignore: tệp .env thật có thể bị đưa lên GitHub"


def test_bug003_env_example_khong_chua_gia_tri_that():
    # .env.example chỉ được ghi giá trị mẫu, không có chuỗi kết nối Atlas thật
    noi_dung = (GOC / ".env.example").read_text(encoding="utf-8")
    assert "mongodb+srv://" not in noi_dung
