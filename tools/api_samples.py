"""Gọi lần lượt các endpoint của hệ thống và ghi lại phản hồi THẬT vào file Markdown.

Cách dùng (hệ thống đang chạy tại http://localhost:8000):
    python tools/api_samples.py
Kết quả ghi vào api-samples.md (trong thư mục đang đứng). Token đăng nhập được che trước khi ghi.

Lưu ý: script TẠO và XÓA dữ liệu thử (một phiếu, một kỹ thuật viên). Chạy xong nên dựng lại
dữ liệu mẫu sạch bằng: docker compose down -v, rồi docker compose up -d --build.
"""
import json
import re
import sys

import httpx

BASE = "http://localhost:8000"
OUT = "api-samples.md"
NV = {"username": "nhanvien01", "password": "NhanVien@2026"}
QL = {"username": "quanly01", "password": "QuanLy@2026"}

lines = []
secrets = []


def mask(text):
    for s in secrets:
        text = text.replace(s, "<token>")
    return text


def find_key(data, key):
    """Tìm giá trị đầu tiên của một khóa trong dữ liệu JSON lồng nhau."""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for v in data.values():
            found = find_key(v, key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for v in data:
            found = find_key(v, key)
            if found is not None:
                return found
    return None


def call(label, method, path, token=None, body=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = httpx.request(method, BASE + path, headers=headers, json=body, timeout=15)
    try:
        data = r.json()
        pretty = json.dumps(data, ensure_ascii=False, indent=2)
    except ValueError:
        data, pretty = None, r.text
    lines.append(f"### {label}\n")
    lines.append(f"Yêu cầu: `{method} {path}`" + (f"  (vai trò/token: có)" if token else "  (không token)"))
    if body is not None:
        shown = json.dumps(body, ensure_ascii=False)
        if "password" in body:
            shown = shown.replace(body["password"], "<mat-khau>")
        lines.append(f"\nThân yêu cầu:\n```json\n{shown}\n```")
    # Danh sách dài chỉ giữ đầu cho gọn
    text = mask(pretty)
    text = re.sub(r'("access_token": ")[^"]+', r'\1<token>', text)
    if len(text) > 2500:
        text = text[:2500] + "\n... (cắt bớt)"
    lines.append(f"\nPhản hồi: **HTTP {r.status_code}**\n```json\n{text}\n```\n")
    print(f"{r.status_code}  {method} {path}  - {label}")
    return r.status_code, data


def login(user):
    code, data = call(f"Đăng nhập {user['username']}", "POST", "/api/auth/login", body=user)
    token = (data or {}).get("access_token")
    if token:
        secrets.append(token)
    return token


def main():
    call("Kiểm tra sức khỏe", "GET", "/health")

    nv = login(NV)
    ql = login(QL)
    if not nv or not ql:
        sys.exit("Không đăng nhập được, dừng.")
    call("Đăng nhập sai mật khẩu", "POST", "/api/auth/login",
         body={"username": "nhanvien01", "password": "sai-mat-khau"})
    call("Đăng nhập thiếu mật khẩu", "POST", "/api/auth/login", body={"username": "nhanvien01"})
    call("Thông tin người đăng nhập", "GET", "/api/auth/me", nv)
    call("Thiếu token", "GET", "/api/auth/me")

    _, cats = call("Danh sách loại lỗi", "GET", "/api/issue-categories", nv)
    cat_id = find_key(cats, "category_id") or 1
    _, techs = call("Danh sách kỹ thuật viên (nhân viên)", "GET", "/api/technicians", nv)
    tech_id = find_key(techs, "technician_id") or 1
    call("Danh sách kỹ thuật viên gồm cả ngừng hoạt động (quản lý)", "GET",
         "/api/technicians?include_inactive=true", ql)

    _, lst = call("Danh sách phiếu (2 phiếu đầu)", "GET", "/api/tickets?size=2", nv)
    call("Lọc phiếu quá hạn", "GET", "/api/tickets?overdue=true&size=1", nv)
    call("Lọc theo trạng thái HOAN_TAT", "GET", "/api/tickets?status=HOAN_TAT&size=1", nv)
    call("Trạng thái lọc không hợp lệ", "GET", "/api/tickets?status=XYZ", nv)
    old_id = find_key(lst, "ticket_id")
    _, detail = call("Chi tiết một phiếu", "GET", f"/api/tickets/{old_id}", nv)
    call("Phiếu không tồn tại", "GET", "/api/tickets/999999", nv)
    phone = find_key(detail, "phone") or find_key(detail, "customer_phone")
    if phone:
        call("Tra cứu khách theo số điện thoại", "GET", f"/api/customers?phone={phone}", nv)
    call("Tra cứu khách không có số", "GET", "/api/customers?phone=0000000000", nv)

    new = {"customer_name": "Khách Thử API", "customer_phone": "0987 654 321",
           "issue_desc": "Màn hình bị sọc ngang sau khi rơi", "priority": "CAO"}
    code, created = call("Tạo phiếu", "POST", "/api/tickets", nv, new)
    tid = (created or {}).get("ticket_id")
    call("Tạo phiếu thiếu số điện thoại", "POST", "/api/tickets", nv,
         {"customer_name": "An", "issue_desc": "Mô tả lỗi đủ mười ký tự"})
    call("Quản lý tạo phiếu (bị chặn)", "POST", "/api/tickets", ql, new)
    call("Phân loại phiếu", "PATCH", f"/api/tickets/{tid}/category", nv, {"category_id": cat_id})
    call("Phân loại với loại lỗi không tồn tại", "PATCH", f"/api/tickets/{tid}/category", nv,
         {"category_id": 99999})
    call("Gán kỹ thuật viên", "PATCH", f"/api/tickets/{tid}/technician", nv,
         {"technician_id": tech_id})
    call("Chuyển trạng thái sang DANG_XU_LY", "PATCH", f"/api/tickets/{tid}/status", nv,
         {"status": "DANG_XU_LY"})
    call("Chuyển trạng thái sai thứ tự", "PATCH", f"/api/tickets/{tid}/status", nv,
         {"status": "MOI"})
    call("Chuyển sang HOAN_TAT", "PATCH", f"/api/tickets/{tid}/status", nv, {"status": "HOAN_TAT"})
    call("Gán kỹ thuật viên cho phiếu đã hoàn tất", "PATCH", f"/api/tickets/{tid}/technician", nv,
         {"technician_id": tech_id})
    call("Tổng quan", "GET", "/api/overview", ql)
    call("Nhân viên xóa phiếu (bị chặn)", "DELETE", f"/api/tickets/{tid}", nv)
    call("Quản lý xóa (ẩn) phiếu", "DELETE", f"/api/tickets/{tid}", ql)
    call("Xem phiếu đã xóa", "GET", f"/api/tickets/{tid}", nv)

    code, tech = call("Thêm kỹ thuật viên", "POST", "/api/technicians", ql,
                      {"technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử"})
    call("Thêm kỹ thuật viên trùng mã", "POST", "/api/technicians", ql,
         {"technician_code": "KT-DEMO", "full_name": "Trùng mã"})
    call("Nhân viên thêm kỹ thuật viên (bị chặn)", "POST", "/api/technicians", nv,
         {"technician_code": "KT-X", "full_name": "Không được"})
    new_tech = (tech or {}).get("technician_id")
    call("Sửa tên kỹ thuật viên", "PATCH", f"/api/technicians/{new_tech}", ql,
         {"full_name": "Kỹ thuật viên thử (đã sửa)"})
    call("Sửa kỹ thuật viên thiếu trường", "PATCH", f"/api/technicians/{new_tech}", ql, {})
    call("Ngừng hoạt động kỹ thuật viên", "DELETE", f"/api/technicians/{new_tech}", ql)

    call("Chưa đăng nhập gọi danh sách phiếu", "GET", "/api/tickets")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# Phản hồi thật của API (tạo bởi tools/api_samples.py)\n\n")
        f.write("\n".join(lines))
    print(f"\nĐã ghi {OUT}. Gửi file này cho mình; không commit file này.")


if __name__ == "__main__":
    main()