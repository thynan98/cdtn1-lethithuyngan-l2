"""Test chạy tay trên hệ thống thật đang chạy ở http://localhost:8000.

Cách dùng:  python tools/manual_checks.py tc09     (hoặc tc10, tc11)
"""
import sys
import time

import httpx
import jwt

BASE = "http://localhost:8000"
# Khóa mặc định ghi sẵn trong docker-compose.yml (ai đọc repo công khai cũng thấy được)
DEFAULT_SECRET = "docker-chay-thu-doi-chuoi-nay-khi-dung-that-0123456789"


def login(username, password):
    r = httpx.post(f"{BASE}/api/auth/login", json={"username": username, "password": password})
    r.raise_for_status()
    return r.json()["access_token"]


def call(method, path, token=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = httpx.request(method, BASE + path, headers=headers, timeout=10, **kwargs)
    print(f"{method} {path}\n  -> HTTP {r.status_code}\n  -> {r.text[:300]}\n")
    return r


def tc09():
    token = login("nhanvien01", "NhanVien@2026")
    print("TC-09: mở phiếu không tồn tại. Mong đợi: 404 NOT_FOUND, không được là 500\n")
    call("GET", "/api/tickets/999999", token)
    call("GET", "/api/tickets/99999999999999999999", token)


def tc10():
    token = login("quanly01", "QuanLy@2026")
    print("TC-10: quản lý tạo phiếu. Mong đợi: 403 FORBIDDEN\n")
    call("POST", "/api/tickets", token, json={
        "customer_name": "An", "customer_phone": "0912345678",
        "issue_desc": "May sac khong vao pin"})


def tc11():
    now = int(time.time())
    fake = jwt.encode({"sub": "2", "username": "quanly01", "name": "Gia mao",
                       "role": "QUAN_LY", "iat": now, "exp": now + 3600},
                      DEFAULT_SECRET, algorithm="HS256")
    print("TC-11: token tự ký bằng khóa mặc định trong repo công khai. "
          "Mong đợi: 401 UNAUTHORIZED\n")
    call("GET", "/api/auth/me", fake)
    call("GET", "/api/overview", fake)


if __name__ == "__main__":
    cases = {"tc09": tc09, "tc10": tc10, "tc11": tc11}
    if len(sys.argv) != 2 or sys.argv[1] not in cases:
        sys.exit("Dùng: python tools/manual_checks.py tc09|tc10|tc11")
    cases[sys.argv[1]]()