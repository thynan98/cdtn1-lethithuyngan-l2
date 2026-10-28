"""Seed: nạp dữ liệu mẫu THẬT của case study (bản mẫu nhỏ trong data/sample/). Chạy lại không nhân đôi.

Chạy:  python -m seeds.seed

Nguồn: bộ dữ liệu của thầy (xem README, mục Dữ liệu mẫu). Việc quy đổi sang thiết kế của em:
  - 5 trạng thái lịch sử -> 3 trạng thái (MOI / DANG_XU_LY / HOAN_TAT), xem STATUS_MAP;
  - hạn cam kết tính lại theo QT-04 (bỏ Chủ nhật) thay cho giờ lịch trong tệp gốc;
  - số điện thoại chuẩn hóa theo QT-01, QT-02; khách trùng số điện thoại chỉ giữ một hồ sơ.
"""
import csv
from datetime import datetime, timezone
from pathlib import Path

from src.database import get_db
from src.repositories.id_generator import next_id
from src.repositories.log_repository import LogRepository
from src.services.auth_service import AuthService
from src.services.ticket_service import calculate_due_date
from src.timeutil import VN
from src.validators.ticket_validator import PHONE_PATTERN, normalize_phone

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

# Tệp chỉ có mã loại lỗi; tên hiển thị tiếng Việt khai báo ở đây
CATEGORY_NAMES = {
    "MAN_HINH": "Màn hình", "PIN": "Pin", "SAC": "Sạc",
    "PHAN_MEM": "Phần mềm", "NUOC_VAO": "Nước vào máy", "KHAC": "Khác",
}
# 5 trạng thái lịch sử -> 3 trạng thái của hệ thống (QT-06 là một chiều MOI -> DANG_XU_LY -> HOAN_TAT)
STATUS_MAP = {
    "MOI": "MOI",
    "DA_PHAN_CONG": "DANG_XU_LY", "DANG_XU_LY": "DANG_XU_LY", "CHO_LINH_KIEN": "DANG_XU_LY",
    "HOAN_TAT": "HOAN_TAT", "DA_DONG": "HOAN_TAT",
}
# Tài khoản demo. Mật khẩu chỉ để chạy thử; trong CSDL chỉ có bản băm.
USERS = [
    ("nhanvien01", "NhanVien@2026", "Võ Thanh Hương", "NHAN_VIEN"),
    ("quanly01", "QuanLy@2026", "Lê Minh Quân", "QUAN_LY"),
]


# ---- hàm thuần (không đụng CSDL, có test) -----------------------------------
def map_status(status):
    return STATUS_MAP[status]


def parse_time(text):
    """'2025-02-23 12:30' (giờ Việt Nam) -> datetime có múi giờ."""
    return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=VN)


def clean_name(raw):
    """Gộp khoảng trắng thừa; tên toàn hoa hoặc toàn thường thì viết hoa chữ đầu mỗi từ."""
    name = " ".join(raw.split())
    return name.title() if name.isupper() or name.islower() else name


def collapse_status_log(rows):
    """Quy đổi nhật ký trạng thái gốc: [(to_status, thời điểm)] đã sắp theo thời gian.

    Các bước liên tiếp rơi vào cùng một trạng thái mới (ví dụ DA_PHAN_CONG rồi DANG_XU_LY)
    chỉ giữ bước đầu. Trả về [(from_status, to_status, thời điểm)].
    """
    result, previous = [], None
    for to_status, when in rows:
        mapped = map_status(to_status)
        if mapped == previous:
            continue
        result.append((previous, mapped, when))
        previous = mapped
    return result


def read_csv(name):
    with open(SAMPLE_DIR / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---- nạp vào CSDL -------------------------------------------------------------
def seed_if_absent(db, collection, key_field, id_field, rows):
    """Chỉ thêm dòng chưa có (so theo khóa nghiệp vụ). Trả về số dòng đã thêm."""
    added = 0
    for row in rows:
        if db[collection].find_one({key_field: row[key_field]}):
            continue
        row[id_field] = next_id(db, collection)
        db[collection].insert_one(row)
        added += 1
    return added


def seed_users(db):
    added = 0
    for username, password, full_name, role in USERS:
        if db.user.find_one({"username": username}):
            continue
        db.user.insert_one({
            "user_id": next_id(db, "user"), "username": username,
            "password_hash": AuthService.hash_password(password),
            "full_name": full_name, "role": role, "is_active": True})
        added += 1
    return added


def seed_customers(db):
    rows, seen = [], set()
    for r in read_csv("customers_sample.csv"):
        phone = normalize_phone(r["so_dien_thoai"])                    # QT-02
        if not PHONE_PATTERN.match(phone) or phone in seen:            # thiếu số hoặc trùng số
            continue
        seen.add(phone)
        created = datetime.strptime(r["ngay_tao"], "%Y-%m-%d").replace(tzinfo=VN)
        rows.append({"phone": phone, "full_name": clean_name(r["ho_ten"]), "created_at": created})
    return seed_if_absent(db, "customer", "phone", "customer_id", rows)


def seed_tickets(db):
    """Nạp phiếu mẫu cùng nhật ký trạng thái và lịch sử gán kỹ thuật viên. Khóa nghiệp vụ: ticket_code."""
    technician_code = {r["technician_id"]: r["technician_code"] for r in read_csv("technicians.csv")}
    category_code = {r["category_id"]: r["category_name"] for r in read_csv("issue_categories.csv")}
    phone_of = {r["record_id"]: normalize_phone(r["so_dien_thoai"]) for r in read_csv("customers_sample.csv")}
    customer_id = {c["phone"]: c["customer_id"] for c in db.customer.find({}, {"_id": 0})}
    tech_id = {t["technician_code"]: t["technician_id"] for t in db.technician.find({}, {"_id": 0})}
    cat_id = {c["category_code"]: c["category_id"] for c in db.issue_category.find({}, {"_id": 0})}

    status_rows = {}
    for r in read_csv("ticket_status_log_sample.csv"):
        status_rows.setdefault(r["ticket_id"], []).append((r["changed_at"], r["to_status"]))

    logs = LogRepository(db)
    added, max_seq = 0, {}
    for t in read_csv("tickets_sample.csv"):
        code = t["ticket_code"]
        seq, year = code.split("-")[1].split("/")
        max_seq[year] = max(max_seq.get(year, 0), int(seq))
        if db.ticket.find_one({"ticket_code": code}):
            continue
        received = parse_time(t["received_at"])
        history = sorted(status_rows.get(t["ticket_id"], []))
        steps = collapse_status_log([(to, parse_time(when)) for when, to in history]) \
            or [(None, map_status(t["status"]), received)]

        ticket_id = next_id(db, "ticket")
        db.ticket.insert_one({
            "ticket_id": ticket_id, "ticket_code": code,
            "customer_id": customer_id[phone_of[t["customer_id"]]],
            "technician_id": tech_id[technician_code[t["technician_id"]]],
            "category_id": cat_id[category_code[t["category_id"]]],
            "issue_desc": t["issue_desc"], "priority": t["priority"],
            "status": steps[-1][1],
            "received_at": received,
            "due_date": calculate_due_date(received, t["priority"]),   # QT-04, tính lại theo ngày làm việc
            "deleted_at": None,
        })
        for from_status, to_status, when in steps:
            logs.add_status(ticket_id, from_status, to_status, when)
        assigned_at = next((parse_time(w) for w, s in history if s == "DA_PHAN_CONG"), received)
        logs.add_assignment(ticket_id, None, tech_id[technician_code[t["technician_id"]]], assigned_at)
        added += 1

    # Bộ đếm mã phiếu phải bằng số lớn nhất đã dùng, để phiếu tạo mới không trùng mã phiếu mẫu
    for year, seq in max_seq.items():
        db.counters.update_one({"_id": f"ticket_code_{year}"}, {"$max": {"seq": seq}}, upsert=True)
    return added


def run(db):
    result = {
        "issue_category": seed_if_absent(db, "issue_category", "category_code", "category_id", [
            {"category_code": r["category_name"], "category_name": CATEGORY_NAMES[r["category_name"]],
             "is_active": r["is_active"] == "true"} for r in read_csv("issue_categories.csv")]),
        "technician": seed_if_absent(db, "technician", "technician_code", "technician_id", [
            {"technician_code": r["technician_code"], "full_name": clean_name(r["ho_ten"]),
             "is_active": r["is_active"] == "true"} for r in read_csv("technicians.csv")]),
        "user": seed_users(db),
        "customer": seed_customers(db),            # phải sau khi có danh mục
    }
    result["ticket"] = seed_tickets(db)            # phải sau customer, technician, issue_category
    for name, added in result.items():
        print(f"[seed] {name}: thêm {added}, hiện có {db[name].count_documents({})}")
    return result


if __name__ == "__main__":
    run(get_db())
