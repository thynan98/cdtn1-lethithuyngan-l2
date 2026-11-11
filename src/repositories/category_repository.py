"""Tầng 3 (lớp repositories) - kho dữ liệu loại lỗi. CHỈ đọc MongoDB."""
from src.repositories.id_generator import is_storable_id

class CategoryRepository:
    def __init__(self, db):
        self.col = db.issue_category

    def list_active(self):
        return list(self.col.find({"is_active": True}, {"_id": 0}).sort("category_id", 1))

    def get(self, category_id):
                if not is_storable_id(category_id):
                      return None
                return self.col.find_one({"category_id": category_id}, {"_id": 0})
