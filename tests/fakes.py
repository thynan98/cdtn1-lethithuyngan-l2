"""Kho dữ liệu GIẢ trong bộ nhớ, có cùng "hình dạng" với các repository thật.

Nhờ tầng service nhận kho qua hàm khởi tạo, test chỉ cần đưa các lớp này vào:
chạy nhanh, không cần MongoDB, và vẫn kiểm được quy tắc nghiệp vụ.
"""
from datetime import datetime, timedelta, timezone

VN = timezone(timedelta(hours=7))


class FakeTickets:
    def __init__(self):
        self.rows = {}
        self.seq = 0
        self.code_seq = 0

    def next_code(self, year):
        self.code_seq += 1
        return f"BH-{self.code_seq:06d}/{year}"

    def insert(self, doc):
        self.seq += 1
        doc = dict(doc, ticket_id=self.seq)
        self.rows[self.seq] = doc
        return dict(doc)

    def get(self, ticket_id, include_deleted=False):
        row = self.rows.get(ticket_id)
        if row is None or (row.get("deleted_at") and not include_deleted):
            return None
        return dict(row)

    def update(self, ticket_id, fields):
        self.rows[ticket_id].update(fields)

    def _live(self):
        return [r for r in self.rows.values() if not r.get("deleted_at")]

    def search(self, status=None, open_only=False, due_before=None, page=1, size=20):
        rows = self._live()
        if status:
            rows = [r for r in rows if r["status"] == status]
        elif open_only:
            rows = [r for r in rows if r["status"] != "HOAN_TAT"]
        if due_before is not None:
            rows = [r for r in rows if r["due_date"] < due_before]
        rows.sort(key=lambda r: (r["received_at"], r["ticket_id"]), reverse=True)
        return [dict(r) for r in rows[(page - 1) * size: page * size]], len(rows)

    def count_by_status(self):
        return {s: sum(1 for r in self._live() if r["status"] == s)
                for s in ("MOI", "DANG_XU_LY", "HOAN_TAT")}

    def count_open(self, due_lt=None, due_gte=None):
        rows = [r for r in self._live() if r["status"] != "HOAN_TAT"]
        if due_lt is not None:
            rows = [r for r in rows if r["due_date"] < due_lt]
        if due_gte is not None:
            rows = [r for r in rows if r["due_date"] >= due_gte]
        return len(rows)

    def list_attention(self, due_lt, limit):
        rows = [r for r in self._live() if r["status"] != "HOAN_TAT" and r["due_date"] < due_lt]
        rows.sort(key=lambda r: r["due_date"])
        return [dict(r) for r in rows[:limit]]

    def list_by_customer(self, customer_id, limit):
        rows = [r for r in self._live() if r["customer_id"] == customer_id]
        rows.sort(key=lambda r: r["received_at"], reverse=True)
        return [dict(r) for r in rows[:limit]]


class FakeCustomers:
    def __init__(self):
        self.rows = {}

    def find_by_phone(self, phone):
        return next((dict(r) for r in self.rows.values() if r["phone"] == phone), None)

    def get(self, customer_id):
        row = self.rows.get(customer_id)
        return dict(row) if row else None

    def get_many(self, ids):
        return {i: dict(self.rows[i]) for i in ids if i in self.rows}

    def insert(self, full_name, phone, created_at):
        cid = len(self.rows) + 1
        self.rows[cid] = {"customer_id": cid, "full_name": full_name, "phone": phone,
                          "created_at": created_at}
        return dict(self.rows[cid])


class FakeTechnicians:
    def __init__(self, rows=()):
        self.rows = {r["technician_id"]: dict(r) for r in rows}

    def list(self, include_inactive=False):
        rows = [r for r in self.rows.values() if include_inactive or r["is_active"]]
        return sorted((dict(r) for r in rows), key=lambda r: r["technician_code"])

    def get(self, technician_id):
        row = self.rows.get(technician_id)
        return dict(row) if row else None

    def get_many(self, ids):
        return {i: dict(self.rows[i]) for i in ids if i in self.rows}

    def find_by_code(self, code):
        return next((dict(r) for r in self.rows.values() if r["technician_code"] == code), None)

    def insert(self, code, full_name):
        tid = max(self.rows, default=0) + 1
        self.rows[tid] = {"technician_id": tid, "technician_code": code,
                          "full_name": full_name, "is_active": True}
        return dict(self.rows[tid])

    def update(self, technician_id, fields):
        self.rows[technician_id].update(fields)


class FakeCategories:
    def __init__(self, rows=()):
        self.rows = {r["category_id"]: dict(r) for r in rows}

    def list_active(self):
        return [dict(r) for r in self.rows.values() if r["is_active"]]

    def get(self, category_id):
        row = self.rows.get(category_id)
        return dict(row) if row else None


class FakeLogs:
    def __init__(self):
        self.status = []
        self.assignment = []

    def add_status(self, ticket_id, from_status, to_status, changed_at):
        self.status.append({"ticket_id": ticket_id, "from_status": from_status,
                            "to_status": to_status, "changed_at": changed_at})

    def add_assignment(self, ticket_id, from_id, to_id, changed_at):
        self.assignment.append({"ticket_id": ticket_id, "from_technician_id": from_id,
                                "to_technician_id": to_id, "changed_at": changed_at})

    def list_status(self, ticket_id):
        return [r for r in self.status if r["ticket_id"] == ticket_id]

    def list_assignment(self, ticket_id):
        return [r for r in self.assignment if r["ticket_id"] == ticket_id]


class FakeUsers:
    def __init__(self, rows=()):
        self.rows = [dict(r) for r in rows]

    def find_by_username(self, username):
        return next((dict(r) for r in self.rows
                     if r["username"] == username and r.get("is_active", True)), None)

    def exists(self, username):
        return any(r["username"] == username for r in self.rows)

    def insert(self, username, password_hash, full_name, role):
        row = {"user_id": len(self.rows) + 1, "username": username, "password_hash": password_hash,
               "full_name": full_name, "role": role, "is_active": True}
        self.rows.append(row)
        return dict(row)


TECHNICIANS = [
    {"technician_id": 1, "technician_code": "KTV001", "full_name": "Nguyễn Văn An", "is_active": True},
    {"technician_id": 2, "technician_code": "KTV002", "full_name": "Trần Thị Bình", "is_active": True},
    {"technician_id": 3, "technician_code": "KTV003", "full_name": "Đã nghỉ việc", "is_active": False},
]
CATEGORIES = [
    {"category_id": 1, "category_code": "MAN_HINH", "category_name": "Màn hình", "is_active": True},
    {"category_id": 2, "category_code": "PIN", "category_name": "Pin", "is_active": True},
]


def at(day, hour=9, minute=0):
    """Thời điểm trong tháng 10/2026, giờ Việt Nam."""
    return datetime(2026, 10, day, hour, minute, tzinfo=VN)
