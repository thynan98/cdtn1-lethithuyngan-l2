"""Seed: nạp dữ liệu mẫu danh mục. Chạy lại không nhân đôi (khóa nghiệp vụ).

Chạy:  python -m seeds.seed
"""
from datetime import datetime, timezone

from src.database import get_db
from src.repositories.id_generator import next_id

ISSUE_CATEGORIES = [
    ("MAN_HINH", "Màn hình"), ("PIN", "Pin"), ("SAC", "Sạc"),
    ("PHAN_MEM", "Phần mềm"), ("NUOC_VAO", "Nước vào máy"), ("KHAC", "Khác"),
]
TECHNICIANS = [
    ("KTV001", "Nguyễn Văn An"), ("KTV002", "Trần Thị Bình"), ("KTV003", "Lê Hoàng Cường"),
    ("KTV004", "Phạm Minh Dũng"), ("KTV005", "Võ Thị Hạnh"),
]
CUSTOMERS = [
    ("0901000001", "Nguyễn Thị Lan"), ("0901000002", "Trần Văn Minh"),
    ("0901000003", "Lê Thị Ngọc"), ("0901000004", "Phạm Quốc Huy"),
    ("0901000005", "Hoàng Thị Mai"), ("0901000006", "Đỗ Văn Phúc"),
    ("0901000007", "Bùi Thị Quyên"), ("0901000008", "Vũ Đức Thắng"),
]


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


def run(db):
    now = datetime.now(timezone.utc)
    result = {
        "issue_category": seed_if_absent(db, "issue_category", "category_code", "category_id", [
            {"category_code": c, "category_name": n, "is_active": True}
            for c, n in ISSUE_CATEGORIES]),
        "technician": seed_if_absent(db, "technician", "technician_code", "technician_id", [
            {"technician_code": c, "full_name": n, "is_active": True}
            for c, n in TECHNICIANS]),
        "customer": seed_if_absent(db, "customer", "phone", "customer_id", [
            {"phone": p, "full_name": n, "created_at": now}
            for p, n in CUSTOMERS]),
    }
    for name, added in result.items():
        print(f"[seed] {name}: thêm {added}, hiện có {db[name].count_documents({})}")
    return result


if __name__ == "__main__":
    run(get_db())
