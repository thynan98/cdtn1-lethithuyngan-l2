import pytest

from src.errors import AppError
from src.services.auth_service import AuthService


def test_password_is_hashed_not_plain():
    stored = AuthService.hash_password("MatKhau@1", iterations=1000)
    assert "MatKhau@1" not in stored
    assert AuthService.verify_password("MatKhau@1", stored)
    assert not AuthService.verify_password("sai", stored)


def test_login_ok_returns_token_and_user(auth):
    result = auth.login({"username": "nv", "password": "MatKhau@1"})
    assert result["user"]["role"] == "NHAN_VIEN"
    assert auth.verify_token(result["access_token"])["username"] == "nv"


@pytest.mark.parametrize("body", [{"username": "nv", "password": "sai"},
                                  {"username": "khong-co", "password": "MatKhau@1"}])
def test_login_wrong_credentials_share_one_message(auth, body):
    with pytest.raises(AppError) as err:
        auth.login(body)
    assert err.value.code == "INVALID_CREDENTIALS"


def test_login_missing_fields_names_them(auth):
    with pytest.raises(AppError) as err:
        auth.login({})
    assert set(err.value.fields) == {"username", "password"}


def test_tampered_token_is_rejected(auth):
    token = auth.login({"username": "nv", "password": "MatKhau@1"})["access_token"]
    with pytest.raises(AppError) as err:
        auth.verify_token(token[:-3] + "abc")
    assert err.value.code == "UNAUTHORIZED"


def test_permissions_follow_srs_roles():
    assert AuthService.can("NHAN_VIEN", "ticket:create")
    assert not AuthService.can("NHAN_VIEN", "ticket:delete")           # SRS: nhân viên không xóa
    assert not AuthService.can("QUAN_LY", "ticket:create")             # SRS: quản lý chỉ xem
    assert AuthService.can("QUAN_LY", "ticket:delete")
    with pytest.raises(AppError) as err:
        AuthService.require("QUAN_LY", "ticket:status")
    assert err.value.code == "FORBIDDEN"
