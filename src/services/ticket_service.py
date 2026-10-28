"""Tầng 3 - nghiệp vụ của phiếu bảo hành.

Quy tắc ở đây KHÔNG biết gì về HTTP (không request, không mã trạng thái) và KHÔNG
biết MongoDB: các kho dữ liệu được đưa vào qua hàm khởi tạo (tiêm phụ thuộc), nên
khi kiểm thử có thể thay bằng kho giả trong bộ nhớ.
"""
import logging
from datetime import timedelta

from src.errors import AppError
from src.timeutil import as_vn, iso_vn, now_vn
from src.validators.ticket_validator import (
    validate_assign_body, validate_category_body, validate_create_ticket,
    validate_list_params, validate_status_body,
)

SLA_WORKING_DAYS = {"CAO": 1, "TRUNG_BINH": 3, "THAP": 5}   # = 24 / 72 / 120 giờ
NEXT_STATUS = {"MOI": "DANG_XU_LY", "DANG_XU_LY": "HOAN_TAT"}
ALL_STATUSES = ("MOI", "DANG_XU_LY", "HOAN_TAT")
SUNDAY = 6          # datetime.weekday(): thứ Hai = 0 ... Chủ nhật = 6
SOON_HOURS = 12     # "sắp đến hạn" = còn không quá 12 giờ (api-contract mục 2)


def calculate_due_date(received_at, priority):
    """QT-04: hạn cam kết = lúc tiếp nhận + 24/72/120 giờ, không tính Chủ nhật."""
    if priority not in SLA_WORKING_DAYS:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"priority": "Mức ưu tiên không hợp lệ"})
    days_left = SLA_WORKING_DAYS[priority]
    due = received_at
    while days_left > 0:
        due += timedelta(days=1)
        if due.weekday() != SUNDAY:      # Chủ nhật không được đếm
            days_left -= 1
    return due


def check_status_transition(current, new):
    """QT-06: chỉ cho chuyển một chiều MOI -> DANG_XU_LY -> HOAN_TAT."""
    if new not in ALL_STATUSES:
        raise AppError("INVALID_FORMAT", "Dữ liệu không hợp lệ",
                       {"status": "Trạng thái không hợp lệ"})
    if NEXT_STATUS.get(current) != new:
        raise AppError("INVALID_TRANSITION", "Sai thứ tự chuyển trạng thái")


def due_state(status, due_date, now):
    """Cảnh báo hạn: QUA_HAN / SAP_DEN_HAN / CON_HAN; phiếu HOAN_TAT thì không cảnh báo.

    Đây là giá trị TÍNH RA từ hạn cam kết và giờ hiện tại, không lưu vào CSDL.
    """
    if status == "HOAN_TAT":
        return None
    due, now = as_vn(due_date), as_vn(now)
    if now > due:
        return "QUA_HAN"
    if due - now <= timedelta(hours=SOON_HOURS):
        return "SAP_DEN_HAN"
    return "CON_HAN"


logger = logging.getLogger(__name__)


class TicketService:
    def __init__(self, tickets, customers, technicians, categories, logs, clock=now_vn):
        self.tickets = tickets
        self.customers = customers
        self.technicians = technicians
        self.categories = categories
        self.logs = logs
        self.clock = clock

    # ---- US1: tạo phiếu -------------------------------------------------
    def create_ticket(self, body, now=None):
        data = validate_create_ticket(body)
        now = now or self.clock()

        # QT-01: mỗi số điện thoại một hồ sơ khách; có rồi thì dùng lại
        customer = self.customers.find_by_phone(data["customer_phone"])
        if customer is None:
            customer = self.customers.insert(data["customer_name"], data["customer_phone"], now)

        ticket = self.tickets.insert({
            "ticket_code": self.tickets.next_code(now.year),
            "customer_id": customer["customer_id"],
            "technician_id": None,
            "category_id": None,
            "issue_desc": data["issue_desc"],
            "priority": data["priority"],
            "status": "MOI",
            "received_at": now,
            "due_date": calculate_due_date(now, data["priority"]),   # QT-04
            "deleted_at": None,
        })
        self.logs.add_status(ticket["ticket_id"], None, "MOI", now)
        # Chỉ ghi mã phiếu và id, không ghi tên hay số điện thoại khách
        logger.info("đã tạo phiếu %s (customer_id=%s)", ticket["ticket_code"], ticket["customer_id"],
                    extra={"ticket_id": ticket["ticket_id"]})
        return {
            "ticket_id": ticket["ticket_id"], "ticket_code": ticket["ticket_code"],
            "customer_id": ticket["customer_id"], "priority": ticket["priority"],
            "status": ticket["status"], "technician_id": None,
            "received_at": iso_vn(ticket["received_at"]), "due_date": iso_vn(ticket["due_date"]),
        }

    # ---- US5: xem một phiếu ---------------------------------------------
    def get_ticket(self, ticket_id, now=None):
        now = now or self.clock()
        t = self._get_or_404(ticket_id)
        customer = self.customers.get(t["customer_id"]) or {}
        technician = self.technicians.get(t["technician_id"]) if t.get("technician_id") else None
        category = self.categories.get(t["category_id"]) if t.get("category_id") else None

        status_history = [
            {"from_status": row.get("from_status"), "to_status": row["to_status"],
             "changed_at": iso_vn(row["changed_at"])}
            for row in self.logs.list_status(ticket_id)]

        assignments = self.logs.list_assignment(ticket_id)
        tech_ids = {x for row in assignments
                    for x in (row.get("from_technician_id"), row["to_technician_id"]) if x}
        names = self.technicians.get_many(tech_ids)
        assignment_history = [
            {"from_technician": _tech_summary(names.get(row.get("from_technician_id"))),
             "to_technician": _tech_summary(names.get(row["to_technician_id"])),
             "changed_at": iso_vn(row["changed_at"])}
            for row in assignments]

        state = due_state(t["status"], t["due_date"], now)
        remaining = None
        if state is not None:
            remaining = int((as_vn(t["due_date"]) - as_vn(now)).total_seconds() // 60)

        return {
            "ticket_id": t["ticket_id"], "ticket_code": t["ticket_code"],
            "customer": {"customer_id": customer.get("customer_id"),
                         "full_name": customer.get("full_name"), "phone": customer.get("phone")},
            "technician": _tech_summary(technician),
            "category": ({"category_id": category["category_id"],
                          "category_code": category["category_code"],
                          "category_name": category["category_name"]} if category else None),
            "issue_desc": t["issue_desc"], "priority": t["priority"], "status": t["status"],
            "received_at": iso_vn(t["received_at"]), "due_date": iso_vn(t["due_date"]),
            "due_state": state, "remaining_minutes": remaining,
            "status_history": status_history, "assignment_history": assignment_history,
        }

    # ---- US6: danh sách và lọc ------------------------------------------
    def list_tickets(self, status=None, overdue=False, page=1, size=20, now=None):
        validate_list_params(status, page, size)
        now = now or self.clock()
        if overdue and status == "HOAN_TAT":
            return {"items": [], "total": 0, "page": page, "size": size}   # đã xong thì không quá hạn

        rows, total = self.tickets.search(
            status=status, open_only=overdue, due_before=now if overdue else None,
            page=page, size=size)
        customers = self.customers.get_many({r["customer_id"] for r in rows})
        technicians = self.technicians.get_many({r["technician_id"] for r in rows if r.get("technician_id")})
        items = [self._row_summary(r, customers, technicians, now) for r in rows]
        return {"items": items, "total": total, "page": page, "size": size}

    # ---- US2: phân loại -------------------------------------------------
    def set_category(self, ticket_id, body):
        category_id = validate_category_body(body)
        self._get_or_404(ticket_id)
        category = self.categories.get(category_id)
        if not category or not category.get("is_active", True):
            raise AppError("NOT_FOUND", "Không tìm thấy loại lỗi")
        self.tickets.update(ticket_id, {"category_id": category_id})
        return {"ticket_id": ticket_id, "category_id": category_id,
                "category_code": category["category_code"]}

    # ---- US3: gán / đổi kỹ thuật viên -----------------------------------
    def assign_technician(self, ticket_id, body, now=None):
        technician_id = validate_assign_body(body)
        now = now or self.clock()
        t = self._get_or_404(ticket_id, "Không tìm thấy phiếu hoặc kỹ thuật viên")
        if t["status"] == "HOAN_TAT":
            raise AppError("TICKET_CLOSED", "Phiếu đã hoàn tất, không thể gán hoặc đổi kỹ thuật viên")
        technician = self.technicians.get(technician_id)
        if not technician or not technician.get("is_active", True):
            raise AppError("NOT_FOUND", "Không tìm thấy phiếu hoặc kỹ thuật viên")

        previous = t.get("technician_id")
        if previous != technician_id:                      # chọn lại đúng người cũ thì không ghi gì
            self.tickets.update(ticket_id, {"technician_id": technician_id})
            self.logs.add_assignment(ticket_id, previous, technician_id, now)
            logger.info("đã gán kỹ thuật viên %s cho phiếu", technician_id, extra={"ticket_id": ticket_id})
        return {"ticket_id": ticket_id, "status": t["status"],
                "technician_id": technician_id, "changed_at": iso_vn(now)}

    # ---- US4: chuyển trạng thái -----------------------------------------
    def change_status(self, ticket_id, body, now=None):
        new_status = validate_status_body(body)
        now = now or self.clock()
        t = self._get_or_404(ticket_id)
        check_status_transition(t["status"], new_status)   # QT-06: kiểm TRƯỚC khi ghi bất cứ thứ gì
        self.tickets.update(ticket_id, {"status": new_status})
        self.logs.add_status(ticket_id, t["status"], new_status, now)
        logger.info("phiếu chuyển %s -> %s", t["status"], new_status, extra={"ticket_id": ticket_id})
        return {"ticket_id": ticket_id, "status": new_status, "changed_at": iso_vn(now)}

    # ---- QT-13: không xóa cứng, chỉ ẩn (xóa mềm) -------------------------
    def delete_ticket(self, ticket_id, now=None):
        now = now or self.clock()
        self._get_or_404(ticket_id)
        self.tickets.update(ticket_id, {"deleted_at": now})
        logger.info("đã ẩn (xóa mềm) phiếu", extra={"ticket_id": ticket_id})
        return {"ticket_id": ticket_id, "deleted_at": iso_vn(now)}

    # ---- Màn Tổng quan --------------------------------------------------
    def overview(self, now=None):
        now = now or self.clock()
        soon = now + timedelta(hours=SOON_HOURS)
        by_status = self.tickets.count_by_status()
        rows = self.tickets.list_attention(due_lt=soon, limit=5)
        customers = self.customers.get_many({r["customer_id"] for r in rows})
        technicians = self.technicians.get_many({r["technician_id"] for r in rows if r.get("technician_id")})
        return {
            "total": sum(by_status.values()),
            "by_status": by_status,
            "overdue": self.tickets.count_open(due_lt=now),
            "near_due": self.tickets.count_open(due_gte=now, due_lt=soon),
            "attention": [self._row_summary(r, customers, technicians, now) for r in rows],
        }

    # ---- hàm phụ ---------------------------------------------------------
    def _get_or_404(self, ticket_id, message="Không tìm thấy phiếu"):
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            raise AppError("NOT_FOUND", message)
        return ticket

    @staticmethod
    def _row_summary(row, customers, technicians, now):
        customer = customers.get(row["customer_id"]) or {}
        technician = technicians.get(row.get("technician_id")) or {}
        return {
            "ticket_id": row["ticket_id"], "ticket_code": row["ticket_code"],
            "customer_name": customer.get("full_name"), "customer_phone": customer.get("phone"),
            "priority": row["priority"], "status": row["status"],
            "technician_name": technician.get("full_name"),
            "due_date": iso_vn(row["due_date"]),
            "due_state": due_state(row["status"], row["due_date"], now),
        }


def _tech_summary(technician):
    if not technician:
        return None
    return {"technician_id": technician["technician_id"],
            "technician_code": technician["technician_code"],
            "full_name": technician["full_name"]}
