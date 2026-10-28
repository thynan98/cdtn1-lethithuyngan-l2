"""Tầng 4 - kho dữ liệu loại lỗi. CHỈ đọc MongoDB."""


class CategoryRepository:
    def __init__(self, db):
        self.col = db.issue_category

    def list_active(self):
        return list(self.col.find({"is_active": True}, {"_id": 0}).sort("category_id", 1))

    def get(self, category_id):
        return self.col.find_one({"category_id": category_id}, {"_id": 0})
