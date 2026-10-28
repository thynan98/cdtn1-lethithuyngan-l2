"""Kiểm thử qua HTTP thật (TestClient) nhưng thay kho dữ liệu bằng kho giả."""
import pytest
from fastapi.testclient import TestClient
from pymongo.errors import ServerSelectionTimeoutError

from src import dependencies as dep
from src.main import app
from src.services.category_service import CategoryService
from src.services.customer_service import CustomerService
from tests.conftest import NEW_TICKET


@pytest.fixture
def client(repos, ticket_service, technician_service, auth):
    app.dependency_overrides[dep.get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[dep.get_technician_service] = lambda: technician_service
    app.dependency_overrides[dep.get_auth_service] = lambda: auth
    app.dependency_overrides[dep.get_customer_service] = lambda: CustomerService(repos["customers"], repos["tickets"])
    app.dependency_overrides[dep.get_category_service] = lambda: CategoryService(repos["categories"])
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def login(client, username, password):
    token = client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff(client):
    return login(client, "nv", "MatKhau@1")


@pytest.fixture
def manager(client):
    return login(client, "ql", "MatKhau@2")


def test_no_token_is_401(client):
    r = client.get("/api/tickets")
    assert r.status_code == 401 and r.json()["error"]["code"] == "UNAUTHORIZED"


def test_wrong_password_is_401(client):
    r = client.post("/api/auth/login", json={"username": "nv", "password": "sai"})
    assert r.status_code == 401 and r.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_create_ticket_returns_201(client, staff):
    r = client.post("/api/tickets", json=NEW_TICKET, headers=staff)
    assert r.status_code == 201 and r.json()["status"] == "MOI"


def test_manager_cannot_create_ticket(client, manager):
    r = client.post("/api/tickets", json=NEW_TICKET, headers=manager)
    assert r.status_code == 403 and r.json()["error"]["code"] == "FORBIDDEN"


def test_invalid_body_is_400_with_field_name(client, staff):
    r = client.post("/api/tickets", json={"customer_name": "An"}, headers=staff)
    assert r.status_code == 400
    assert "customer_phone" in r.json()["error"]["fields"]


def test_non_json_body_is_400(client, staff):
    r = client.post("/api/tickets", content="khong phai json", headers=staff)
    assert r.status_code == 400 and r.json()["error"]["code"] == "INVALID_FORMAT"


def test_skip_status_is_409(client, staff):
    tid = client.post("/api/tickets", json=NEW_TICKET, headers=staff).json()["ticket_id"]
    r = client.patch(f"/api/tickets/{tid}/status", json={"status": "HOAN_TAT"}, headers=staff)
    assert r.status_code == 409 and r.json()["error"]["code"] == "INVALID_TRANSITION"


def test_unknown_ticket_is_404(client, staff):
    assert client.get("/api/tickets/999", headers=staff).status_code == 404


def test_only_manager_can_delete_and_ticket_disappears(client, staff, manager):
    tid = client.post("/api/tickets", json=NEW_TICKET, headers=staff).json()["ticket_id"]
    assert client.delete(f"/api/tickets/{tid}", headers=staff).status_code == 403
    assert client.delete(f"/api/tickets/{tid}", headers=manager).status_code == 200
    assert client.get(f"/api/tickets/{tid}", headers=manager).status_code == 404


def test_list_and_overview(client, staff):
    client.post("/api/tickets", json=NEW_TICKET, headers=staff)
    assert client.get("/api/tickets", headers=staff).json()["total"] == 1
    assert client.get("/api/overview", headers=staff).json()["total"] == 1


def test_technician_management_is_manager_only(client, staff, manager):
    body = {"technician_code": "ktv050", "full_name": "Kỹ Thuật Mới"}
    assert client.post("/api/technicians", json=body, headers=staff).status_code == 403
    assert client.post("/api/technicians", json=body, headers=manager).status_code == 201
    assert client.post("/api/technicians", json=body, headers=manager).status_code == 409


def test_customer_lookup_and_categories(client, staff):
    client.post("/api/tickets", json=NEW_TICKET, headers=staff)
    r = client.get("/api/customers", params={"phone": "+84 901 000 001"}, headers=staff)
    assert r.status_code == 200 and len(r.json()["tickets"]) == 1
    assert client.get("/api/customers", params={"phone": "123"}, headers=staff).status_code == 400
    assert len(client.get("/api/issue-categories", headers=staff).json()["items"]) == 2


def test_database_down_is_503_without_leaking_details(client, staff, ticket_service):
    def boom(*a, **k):
        raise ServerSelectionTimeoutError("mongodb+srv://user:matkhau@cluster/ timed out")
    ticket_service.list_tickets = boom
    r = client.get("/api/tickets", headers=staff)
    assert r.status_code == 503 and r.json()["error"]["code"] == "DB_UNAVAILABLE"
    assert "matkhau" not in r.text and "mongodb" not in r.text
