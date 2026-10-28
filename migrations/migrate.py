"""Migration: dựng collection, validator và chỉ mục theo docs/data-model.md.

Chạy:  python -m migrations.migrate
Chạy lại nhiều lần vẫn an toàn (idempotent).
"""
from src.database import get_db

INT = ["int", "long"]          # Python int có thể được lưu là int32 hoặc int64
NULLABLE_INT = INT + ["null"]

COLLECTIONS = {
    "customer": {
        "required": ["customer_id", "full_name", "phone", "created_at"],
        "properties": {
            "customer_id": {"bsonType": INT},
            "full_name": {"bsonType": "string", "maxLength": 120},
            "phone": {"bsonType": "string", "pattern": "^0[0-9]{9}$"},  # QT-01, QT-02
            "created_at": {"bsonType": "date"},
        },
        "indexes": [([("customer_id", 1)], True), ([("phone", 1)], True)],
    },
    "technician": {
        "required": ["technician_id", "technician_code", "full_name", "is_active"],
        "properties": {
            "technician_id": {"bsonType": INT},
            "technician_code": {"bsonType": "string", "maxLength": 20},
            "full_name": {"bsonType": "string", "maxLength": 120},
            "is_active": {"bsonType": "bool"},
        },
        "indexes": [([("technician_id", 1)], True), ([("technician_code", 1)], True)],
    },
    "issue_category": {
        "required": ["category_id", "category_code", "category_name", "is_active"],
        "properties": {
            "category_id": {"bsonType": INT},
            "category_code": {"bsonType": "string", "maxLength": 20},
            "category_name": {"bsonType": "string", "maxLength": 60},
            "is_active": {"bsonType": "bool"},
        },
        "indexes": [([("category_id", 1)], True), ([("category_code", 1)], True)],
    },
    "ticket": {
        "required": ["ticket_id", "ticket_code", "customer_id", "issue_desc",
                     "priority", "status", "received_at", "due_date"],
        "properties": {
            "ticket_id": {"bsonType": INT},
            "ticket_code": {"bsonType": "string", "maxLength": 20},   # NFR-03
            "customer_id": {"bsonType": INT},
            "technician_id": {"bsonType": NULLABLE_INT},
            "category_id": {"bsonType": NULLABLE_INT},
            "issue_desc": {"bsonType": "string", "minLength": 10, "maxLength": 2000},
            "priority": {"enum": ["CAO", "TRUNG_BINH", "THAP"]},
            "status": {"enum": ["MOI", "DANG_XU_LY", "HOAN_TAT"]},    # QT-06
            "received_at": {"bsonType": "date"},
            "due_date": {"bsonType": "date"},                         # QT-04
            "deleted_at": {"bsonType": ["date", "null"]},             # xóa mềm (TD-06)
        },
        "indexes": [
            ([("ticket_id", 1)], True),
            ([("ticket_code", 1)], True),
            ([("status", 1), ("due_date", 1)], False),                # NFR-04
            ([("customer_id", 1)], False),                            # tra cứu theo khách (US7)
        ],
    },
    "user": {                                                         # tài khoản đăng nhập (TD-05)
        "required": ["user_id", "username", "password_hash", "full_name", "role", "is_active"],
        "properties": {
            "user_id": {"bsonType": INT},
            "username": {"bsonType": "string", "maxLength": 50},
            "password_hash": {"bsonType": "string"},                  # KHÔNG lưu mật khẩu chữ thường
            "full_name": {"bsonType": "string", "maxLength": 120},
            "role": {"enum": ["NHAN_VIEN", "QUAN_LY"]},
            "is_active": {"bsonType": "bool"},
        },
        "indexes": [([("user_id", 1)], True), ([("username", 1)], True)],
    },
    "ticket_status_log": {
        "required": ["log_id", "ticket_id", "to_status", "changed_at"],
        "properties": {
            "log_id": {"bsonType": INT},
            "ticket_id": {"bsonType": INT},
            "from_status": {"bsonType": ["string", "null"]},
            "to_status": {"bsonType": "string"},
            "changed_at": {"bsonType": "date"},
        },
        "indexes": [([("log_id", 1)], True), ([("ticket_id", 1), ("changed_at", 1)], False)],
    },
    "ticket_assignment_log": {
        "required": ["log_id", "ticket_id", "to_technician_id", "changed_at"],
        "properties": {
            "log_id": {"bsonType": INT},
            "ticket_id": {"bsonType": INT},
            "from_technician_id": {"bsonType": NULLABLE_INT},
            "to_technician_id": {"bsonType": INT},
            "changed_at": {"bsonType": "date"},
        },
        "indexes": [([("log_id", 1)], True), ([("ticket_id", 1), ("changed_at", 1)], False)],
    },
}


def migrate(db):
    """Tạo collection nếu chưa có, cập nhật validator nếu đã có, rồi tạo chỉ mục."""
    existing = set(db.list_collection_names())
    for name, spec in COLLECTIONS.items():
        validator = {"$jsonSchema": {
            "bsonType": "object",
            "required": spec["required"],
            "properties": spec["properties"],
        }}
        if name in existing:
            db.command("collMod", name, validator=validator)
        else:
            db.create_collection(name, validator=validator)
        for keys, unique in spec["indexes"]:
            db[name].create_index(keys, unique=unique)   # tạo lại chỉ mục giống hệt thì không lỗi
        print(f"[migrate] {name}: OK")


if __name__ == "__main__":
    migrate(get_db())
