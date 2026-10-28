"""Tầng 2 (lớp services) - nghiệp vụ danh sách loại lỗi (US2): chỉ đọc, trả về các loại lỗi đang dùng."""


class CategoryService:
    def __init__(self, categories):
        self.categories = categories

    def list_categories(self):
        return {"items": [{"category_id": c["category_id"], "category_code": c["category_code"],
                           "category_name": c["category_name"]} for c in self.categories.list_active()]}
