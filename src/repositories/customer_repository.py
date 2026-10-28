"""Tầng 3 (lớp repositories) - kho dữ liệu khách hàng. CHỈ đọc/ghi MongoDB."""
from src.repositories.id_generator import next_id


class CustomerRepository:
    def __init__(self, db):
        self.db = db
        self.col = db.customer

    def find_by_phone(self, phone):
        return self.col.find_one({"phone": phone}, {"_id": 0})

    def get(self, customer_id):
        return self.col.find_one({"customer_id": customer_id}, {"_id": 0})

    def get_many(self, ids):
        """Trả về dict {customer_id: hồ sơ} cho một tập mã khách."""
        ids = list(ids)
        if not ids:
            return {}
        rows = self.col.find({"customer_id": {"$in": ids}}, {"_id": 0})
        return {row["customer_id"]: row for row in rows}

    def insert(self, full_name, phone, created_at):
        doc = {"customer_id": next_id(self.db, "customer"), "full_name": full_name,
               "phone": phone, "created_at": created_at}
        self.col.insert_one(dict(doc))
        return doc
