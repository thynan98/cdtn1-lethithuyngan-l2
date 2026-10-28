"""Kiểm thử log và mã tra cứu: lỗi hệ thống không lộ chi tiết kỹ thuật, log không chứa dữ liệu nhạy cảm."""
import json
import logging

import pytest
from fastapi.testclient import TestClient

from src import dependencies as dep
from src.logging_config import JsonFormatter, request_id_var
from src.main import app
from tests.conftest import NEW_TICKET
from tests.test_api import client, login, staff  # noqa: F401  (dùng lại fixture)


def test_response_has_request_id_header(client):
    r = client.get("/health", headers={"X-Request-Id": "abc12345"})
    assert r.headers["X-Request-Id"] == "abc12345"            # giữ mã do bên gọi gửi
    assert client.get("/health").headers["X-Request-Id"]      # không gửi thì hệ thống tự sinh


def test_system_error_shows_reference_code_but_no_stack(client):
    def broken():
        raise RuntimeError("secret-internal-detail")
    app.dependency_overrides[dep.get_ticket_service] = broken
    token = client.post("/api/auth/login", json={"username": "nv", "password": "MatKhau@1"}).json()["access_token"]
    r = client.get("/api/tickets", headers={"Authorization": f"Bearer {token}", "X-Request-Id": "tra-cuu-01"})
    body = r.json()["error"]
    assert r.status_code == 500 and body["code"] == "INTERNAL_ERROR"
    assert "tra-cuu-01" in body["message"]                      # có mã tra cứu để người dùng báo lại
    assert "secret-internal-detail" not in r.text               # không lộ chi tiết kỹ thuật


def test_log_line_is_json_and_has_required_fields():
    token = request_id_var.set("rid-test")
    try:
        record = logging.LogRecord("x", logging.INFO, __file__, 1, "đã tạo phiếu %s", ("BH-000001/2026",), None)
        record.ticket_id = 7
        line = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)
    assert line["muc"] == "INFO" and line["request_id"] == "rid-test" and line["ticket_id"] == 7
    assert "+07:00" in line["thoi_diem"] and "BH-000001/2026" in line["thong_diep"]


def test_create_ticket_log_has_no_phone_or_name(ticket_service, caplog):
    with caplog.at_level(logging.INFO):
        ticket_service.create_ticket(dict(NEW_TICKET))
    text = " ".join(r.getMessage() for r in caplog.records)
    assert "đã tạo phiếu" in text
    assert NEW_TICKET["customer_phone"] not in text and NEW_TICKET["customer_name"] not in text
