"""Kiểm thử tầng service bằng kho giả: không MongoDB, không HTTP."""
import pytest

from src.errors import AppError
from tests.conftest import NEW_TICKET
from tests.fakes import at


def code_of(err):
    return err.value.code


# ---- luồng đúng ------------------------------------------------------------
def test_create_ticket_sets_due_date_and_first_log(ticket_service, repos):
    created = ticket_service.create_ticket(NEW_TICKET)
    assert created["status"] == "MOI"
    assert created["ticket_code"] == "BH-000001/2026"
    assert created["due_date"] == "2026-10-08T09:00:00+07:00"      # thứ Hai 05/10 + 3 ngày làm việc
    assert repos["logs"].list_status(created["ticket_id"])[0]["to_status"] == "MOI"


def test_same_phone_reuses_customer_profile(ticket_service, repos):
    ticket_service.create_ticket(NEW_TICKET)
    ticket_service.create_ticket(dict(NEW_TICKET, issue_desc="Pin chai nhanh lắm"))
    assert len(repos["customers"].rows) == 1                          # QT-01


def test_full_flow_assign_classify_and_close(ticket_service):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    ticket_service.set_category(tid, {"category_id": 1})
    ticket_service.assign_technician(tid, {"technician_id": 1})
    ticket_service.change_status(tid, {"status": "DANG_XU_LY"})
    ticket_service.change_status(tid, {"status": "HOAN_TAT"})
    detail = ticket_service.get_ticket(tid)
    assert detail["status"] == "HOAN_TAT"
    assert detail["due_state"] is None                                # phiếu xong thì không cảnh báo
    assert [h["to_status"] for h in detail["status_history"]] == ["MOI", "DANG_XU_LY", "HOAN_TAT"]
    assert detail["category"]["category_code"] == "MAN_HINH"


def test_reassign_writes_history_but_same_technician_does_not(ticket_service, repos):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    ticket_service.assign_technician(tid, {"technician_id": 1})
    ticket_service.assign_technician(tid, {"technician_id": 1})       # chọn lại đúng người cũ
    ticket_service.assign_technician(tid, {"technician_id": 2})
    assert len(repos["logs"].list_assignment(tid)) == 2


# ---- biên ------------------------------------------------------------------
def test_due_state_near_due_and_overdue(ticket_service):
    tid = ticket_service.create_ticket(dict(NEW_TICKET, priority="CAO"))["ticket_id"]   # hạn 06/10 09:00
    assert ticket_service.get_ticket(tid, now=at(5, 10))["due_state"] == "CON_HAN"
    assert ticket_service.get_ticket(tid, now=at(5, 21))["due_state"] == "SAP_DEN_HAN"  # còn 12 giờ
    assert ticket_service.get_ticket(tid, now=at(6, 9, 1))["due_state"] == "QUA_HAN"


def test_overdue_filter_lists_only_open_late_tickets(ticket_service):
    late = ticket_service.create_ticket(dict(NEW_TICKET, priority="CAO"))["ticket_id"]
    ticket_service.create_ticket(dict(NEW_TICKET, priority="THAP", issue_desc="Loa bị rè khi nghe"))
    result = ticket_service.list_tickets(overdue=True, now=at(7))
    assert [i["ticket_id"] for i in result["items"]] == [late]


def test_overview_counts(ticket_service):
    ticket_service.create_ticket(dict(NEW_TICKET, priority="CAO"))
    done = ticket_service.create_ticket(dict(NEW_TICKET, issue_desc="Loa bị rè khi nghe"))["ticket_id"]
    ticket_service.change_status(done, {"status": "DANG_XU_LY"})
    data = ticket_service.overview(now=at(7))
    assert data["total"] == 2
    assert data["by_status"] == {"MOI": 1, "DANG_XU_LY": 1, "HOAN_TAT": 0}
    assert data["overdue"] == 1
    assert len(data["attention"]) == 1


# ---- dữ liệu sai -------------------------------------------------------------
def test_create_with_missing_phone_is_rejected(ticket_service):
    with pytest.raises(AppError) as err:
        ticket_service.create_ticket({"customer_name": "An", "issue_desc": "Máy sạc không vào"})
    assert code_of(err) == "REQUIRED_FIELD_MISSING"


def test_cannot_skip_status_and_nothing_is_logged(ticket_service, repos):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    with pytest.raises(AppError) as err:
        ticket_service.change_status(tid, {"status": "HOAN_TAT"})
    assert code_of(err) == "INVALID_TRANSITION"
    assert len(repos["logs"].list_status(tid)) == 1                   # chỉ còn dòng "tạo phiếu"


def test_closed_ticket_cannot_be_reassigned(ticket_service):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    ticket_service.change_status(tid, {"status": "DANG_XU_LY"})
    ticket_service.change_status(tid, {"status": "HOAN_TAT"})
    with pytest.raises(AppError) as err:
        ticket_service.assign_technician(tid, {"technician_id": 1})
    assert code_of(err) == "TICKET_CLOSED"


def test_inactive_or_unknown_technician_is_not_found(ticket_service):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    for bad in (3, 99):                                               # 3 = đã nghỉ việc
        with pytest.raises(AppError) as err:
            ticket_service.assign_technician(tid, {"technician_id": bad})
        assert code_of(err) == "NOT_FOUND"


def test_unknown_ticket_is_not_found(ticket_service):
    with pytest.raises(AppError) as err:
        ticket_service.get_ticket(999)
    assert code_of(err) == "NOT_FOUND"


def test_soft_delete_hides_ticket_but_keeps_data(ticket_service, repos):
    tid = ticket_service.create_ticket(NEW_TICKET)["ticket_id"]
    ticket_service.delete_ticket(tid)
    with pytest.raises(AppError):
        ticket_service.get_ticket(tid)
    assert ticket_service.list_tickets()["total"] == 0
    assert repos["tickets"].get(tid, include_deleted=True) is not None   # QT-13: dữ liệu còn nguyên


def test_bad_list_params_are_rejected(ticket_service):
    with pytest.raises(AppError) as err:
        ticket_service.list_tickets(status="LUNG_TUNG")
    assert code_of(err) == "INVALID_FORMAT"
