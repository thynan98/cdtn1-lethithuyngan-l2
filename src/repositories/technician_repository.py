"""Tầng 3 (lớp repositories) - kho dữ liệu kỹ thuật viên. CHỈ đọc/ghi MongoDB.

Không xóa cứng (QT-13): "ngừng hoạt động" chỉ đặt is_active = False.
"""
from src.repositories.id_generator import next_id


class TechnicianRepository:
    def __init__(self, db):
        self.db = db
        self.col = db.technician

    def list(self, include_inactive=False):
        query = {} if include_inactive else {"is_active": True}
        return list(self.col.find(query, {"_id": 0}).sort("technician_code", 1))

    def get(self, technician_id):
        return self.col.find_one({"technician_id": technician_id}, {"_id": 0})

    def get_many(self, ids):
        ids = list(ids)
        if not ids:
            return {}
        rows = self.col.find({"technician_id": {"$in": ids}}, {"_id": 0})
        return {row["technician_id"]: row for row in rows}

    def find_by_code(self, code):
        return self.col.find_one({"technician_code": code}, {"_id": 0})

    def insert(self, code, full_name):
        doc = {"technician_id": next_id(self.db, "technician"), "technician_code": code,
               "full_name": full_name, "is_active": True}
        self.col.insert_one(dict(doc))
        return doc

    def update(self, technician_id, fields):
        self.col.update_one({"technician_id": technician_id}, {"$set": fields})
