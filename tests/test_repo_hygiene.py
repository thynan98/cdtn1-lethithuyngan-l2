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



# ---- Hồi quy cho BUG-005: khóa ký token (JWT_SECRET) không được có giá trị mặc định trong repo ----
def test_bug005_compose_khong_co_khoa_mac_dinh():
    dong = [d for d in doc_dong("docker-compose.yml") if d.startswith("JWT_SECRET:")]
    assert dong, "docker-compose.yml phải truyền JWT_SECRET cho dịch vụ app"
    assert ":-" not in dong[0], "JWT_SECRET trong compose không được có giá trị mặc định (repo công khai)"


def test_bug005_config_khong_co_khoa_mac_dinh():
    noi_dung = (GOC / "src" / "config.py").read_text(encoding="utf-8")
    assert "_DEV_SECRET" not in noi_dung, "src/config.py không được giữ khóa chạy thử"


def test_bug005_env_example_co_khoa_mau_du_dai():
    gia_tri = [d.split("=", 1)[1] for d in doc_dong(".env.example") if d.startswith("JWT_SECRET=")]
    assert gia_tri and len(gia_tri[0]) >= 32, "JWT_SECRET mẫu trong .env.example phải dài ít nhất 32 ký tự"