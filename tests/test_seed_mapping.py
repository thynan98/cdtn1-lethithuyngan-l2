"""Kiểm thử phần quy đổi dữ liệu gốc của thầy sang thiết kế của em (hàm thuần, không cần CSDL)."""
from datetime import datetime

from seeds.seed import clean_name, collapse_status_log, map_status, parse_time, read_csv
from src.timeutil import VN
from src.validators.ticket_validator import PHONE_PATTERN, normalize_phone


def test_five_legacy_statuses_map_to_three():
    assert [map_status(s) for s in ("DA_PHAN_CONG", "CHO_LINH_KIEN", "DA_DONG")] == \
        ["DANG_XU_LY", "DANG_XU_LY", "HOAN_TAT"]


def test_collapse_keeps_first_step_of_each_run():
    t = lambda h: datetime(2025, 2, 23, h, 0, tzinfo=VN)
    steps = collapse_status_log([("MOI", t(8)), ("DA_PHAN_CONG", t(9)), ("DANG_XU_LY", t(10)),
                                 ("CHO_LINH_KIEN", t(11)), ("DANG_XU_LY", t(12)),
                                 ("HOAN_TAT", t(13)), ("DA_DONG", t(14))])
    assert [(a, b) for a, b, _ in steps] == [(None, "MOI"), ("MOI", "DANG_XU_LY"), ("DANG_XU_LY", "HOAN_TAT")]
    assert steps[1][2] == t(9)                         # giữ thời điểm của bước đầu trong cụm


def test_clean_name_and_time():
    assert clean_name("  NGUYỄN   VĂN AN ") == "Nguyễn Văn An"
    assert clean_name("Phan Hữu Bình") == "Phan Hữu Bình"
    assert parse_time("2025-02-23 12:30").utcoffset().total_seconds() == 7 * 3600


def test_sample_files_are_usable():
    tickets = read_csv("tickets_sample.csv")
    assert len(tickets) == 60
    assert all(len(t["issue_desc"]) >= 10 for t in tickets)          # đúng ràng buộc 10 ký tự
    phones = {c["record_id"]: normalize_phone(c["so_dien_thoai"]) for c in read_csv("customers_sample.csv")}
    assert all(PHONE_PATTERN.match(phones[t["customer_id"]]) for t in tickets)
