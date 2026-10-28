"""Tầng 4 - kho dữ liệu tài khoản đăng nhập. CHỈ đọc/ghi MongoDB."""
from src.repositories.id_generator import next_id


class UserRepository:
    def __init__(self, db):
        self.db = db
        self.col = db.user

    def find_by_username(self, username):
        """Chỉ trả về tài khoản còn hoạt động."""
        return self.col.find_one({"username": username, "is_active": True}, {"_id": 0})

    def exists(self, username):
        return self.col.count_documents({"username": username}) > 0

    def insert(self, username, password_hash, full_name, role):
        doc = {"user_id": next_id(self.db, "user"), "username": username,
               "password_hash": password_hash, "full_name": full_name,
               "role": role, "is_active": True}
        self.col.insert_one(dict(doc))
        return doc
