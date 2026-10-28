"""Tầng 3 (lớp repositories) - kho dữ liệu của phiếu. CHỈ đọc/ghi MongoDB, không chứa quy tắc nghiệp vụ.

Phiếu "đã xóa mềm" có deleted_at khác rỗng; mọi truy vấn mặc định bỏ qua các phiếu này.
"""
from src.repositories.id_generator import next_id


class TicketRepository:
    def __init__(self, db):
        self.db = db
        self.col = db.ticket

    def next_code(self, year):
        """Mã phiếu dạng BH-000231/2026 (NFR-03); số thứ tự tăng riêng cho từng năm."""
        seq = next_id(self.db, f"ticket_code_{year}")
        return f"BH-{seq:06d}/{year}"

    def insert(self, doc):
        doc = dict(doc)
        doc["ticket_id"] = next_id(self.db, "ticket")
        self.col.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def get(self, ticket_id, include_deleted=False):
        query = {"ticket_id": ticket_id}
        if not include_deleted:
            query["deleted_at"] = None
        return self.col.find_one(query, {"_id": 0})

    def update(self, ticket_id, fields):
        self.col.update_one({"ticket_id": ticket_id}, {"$set": fields})

    def search(self, status=None, open_only=False, due_before=None, page=1, size=20):
        """Trả về (danh sách phiếu của một trang, tổng số phiếu khớp), mới nhất trước.

        status     : chỉ lấy phiếu ở trạng thái này
        open_only  : chỉ lấy phiếu chưa HOAN_TAT (dùng khi status không được chỉ định)
        due_before : chỉ lấy phiếu có hạn cam kết trước thời điểm này
        """
        query = {"deleted_at": None}
        if status:
            query["status"] = status
        elif open_only:
            query["status"] = {"$ne": "HOAN_TAT"}
        if due_before is not None:
            query["due_date"] = {"$lt": due_before}
        total = self.col.count_documents(query)
        cursor = (self.col.find(query, {"_id": 0})
                  .sort([("received_at", -1), ("ticket_id", -1)])
                  .skip((page - 1) * size).limit(size))
        return list(cursor), total

    def count_by_status(self):
        return {s: self.col.count_documents({"deleted_at": None, "status": s})
                for s in ("MOI", "DANG_XU_LY", "HOAN_TAT")}

    def count_open(self, due_lt=None, due_gte=None):
        """Đếm phiếu chưa hoàn tất theo khoảng hạn cam kết [due_gte, due_lt)."""
        query = {"deleted_at": None, "status": {"$ne": "HOAN_TAT"}}
        due = {}
        if due_lt is not None:
            due["$lt"] = due_lt
        if due_gte is not None:
            due["$gte"] = due_gte
        if due:
            query["due_date"] = due
        return self.col.count_documents(query)

    def list_attention(self, due_lt, limit):
        """Phiếu chưa hoàn tất có hạn trước due_lt, hạn gần nhất lên đầu."""
        query = {"deleted_at": None, "status": {"$ne": "HOAN_TAT"}, "due_date": {"$lt": due_lt}}
        return list(self.col.find(query, {"_id": 0}).sort("due_date", 1).limit(limit))

    def list_by_customer(self, customer_id, limit):
        query = {"deleted_at": None, "customer_id": customer_id}
        return list(self.col.find(query, {"_id": 0}).sort("received_at", -1).limit(limit))
