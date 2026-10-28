"""Tầng 3 (lớp repositories) - kho nhật ký: lịch sử chuyển trạng thái và lịch sử đổi kỹ thuật viên."""
from src.repositories.id_generator import next_id


class LogRepository:
    def __init__(self, db):
        self.db = db

    def add_status(self, ticket_id, from_status, to_status, changed_at):
        self.db.ticket_status_log.insert_one({
            "log_id": next_id(self.db, "ticket_status_log"), "ticket_id": ticket_id,
            "from_status": from_status, "to_status": to_status, "changed_at": changed_at})

    def add_assignment(self, ticket_id, from_technician_id, to_technician_id, changed_at):
        self.db.ticket_assignment_log.insert_one({
            "log_id": next_id(self.db, "ticket_assignment_log"), "ticket_id": ticket_id,
            "from_technician_id": from_technician_id, "to_technician_id": to_technician_id,
            "changed_at": changed_at})

    def list_status(self, ticket_id):
        rows = self.db.ticket_status_log.find({"ticket_id": ticket_id}, {"_id": 0})
        return list(rows.sort([("changed_at", 1), ("log_id", 1)]))

    def list_assignment(self, ticket_id):
        rows = self.db.ticket_assignment_log.find({"ticket_id": ticket_id}, {"_id": 0})
        return list(rows.sort([("changed_at", 1), ("log_id", 1)]))
