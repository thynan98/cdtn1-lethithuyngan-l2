"""Tầng 2 (lớp services) - đăng nhập cơ bản và phân quyền nhẹ (TD-05).

- Mật khẩu KHÔNG lưu chữ thường: băm bằng PBKDF2-SHA256 kèm muối ngẫu nhiên.
- Đăng nhập đúng thì cấp token JWT (có hạn); mỗi lần gọi API trình duyệt gửi lại token.
- Hai vai trò, mỗi vai trò có danh sách quyền (bảng PERMISSIONS bên dưới).
Tầng này không biết gì về HTTP: lỗi được ném ra dưới dạng AppError có mã.
"""
import hashlib
import hmac
import secrets
from datetime import timedelta

import jwt

from src.errors import AppError
from src.timeutil import now_vn

PBKDF2_ITERATIONS = 200_000

# Quyền theo vai trò. Khớp cột "Không được làm" trong SRS 2.1:
#  - Nhân viên tiếp nhận: tạo phiếu, phân loại, gán kỹ thuật viên, đổi trạng thái; KHÔNG xóa.
#  - Quản lý trung tâm: chỉ xem; KHÔNG tạo, gán hay đổi trạng thái (TD-06: thêm ẩn phiếu
#    và quản lý kỹ thuật viên cho vai trò này).
PERMISSIONS = {
    "NHAN_VIEN": {"ticket:view", "ticket:create", "ticket:classify", "ticket:assign",
                  "ticket:status", "customer:view", "technician:view", "overview:view"},
    "QUAN_LY": {"ticket:view", "ticket:delete", "customer:view", "technician:view",
                "technician:manage", "overview:view"},
}


class AuthService:
    def __init__(self, users, secret, expire_minutes=480, clock=now_vn):
        self.users = users
        self.secret = secret
        self.expire_minutes = expire_minutes
        self.clock = clock

    # ---- mật khẩu ---------------------------------------------------------
    @staticmethod
    def hash_password(password, iterations=PBKDF2_ITERATIONS):
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                     bytes.fromhex(salt), iterations).hex()
        return f"pbkdf2_sha256${iterations}${salt}${digest}"

    @staticmethod
    def verify_password(password, stored):
        try:
            scheme, iterations, salt, digest = stored.split("$")
            if scheme != "pbkdf2_sha256":
                return False
            check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                        bytes.fromhex(salt), int(iterations)).hex()
        except (ValueError, AttributeError):
            return False
        return hmac.compare_digest(check, digest)     # so sánh không lộ thời gian

    # ---- đăng nhập / token --------------------------------------------------
    def login(self, body):
        body = body or {}
        username = str(body.get("username") or "").strip()
        password = str(body.get("password") or "")
        missing = {}
        if not username:
            missing["username"] = "Vui lòng nhập tên đăng nhập"
        if not password:
            missing["password"] = "Vui lòng nhập mật khẩu"
        if missing:
            raise AppError("REQUIRED_FIELD_MISSING", "Dữ liệu không hợp lệ", missing)

        user = self.users.find_by_username(username)
        # Cùng một thông báo cho "sai tên" và "sai mật khẩu" để không lộ tài khoản nào tồn tại
        if user is None or not self.verify_password(password, user["password_hash"]):
            raise AppError("INVALID_CREDENTIALS", "Sai tên đăng nhập hoặc mật khẩu")

        now = self.clock()
        token = jwt.encode({
            "sub": str(user["user_id"]), "username": user["username"],
            "name": user["full_name"], "role": user["role"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.expire_minutes)).timestamp()),
        }, self.secret, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer",
                "expires_in": self.expire_minutes * 60,
                "user": {"username": user["username"], "full_name": user["full_name"],
                         "role": user["role"]}}

    def verify_token(self, token):
        """Trả về thông tin người dùng trong token, hoặc ném UNAUTHORIZED."""
        try:
            claims = jwt.decode(token, self.secret, algorithms=["HS256"])
            return {"user_id": int(claims["sub"]), "username": claims["username"],
                    "full_name": claims["name"], "role": claims["role"]}
        except (jwt.PyJWTError, KeyError, ValueError):
            raise AppError("UNAUTHORIZED", "Phiên đăng nhập đã hết hạn hoặc không hợp lệ")

    # ---- phân quyền -----------------------------------------------------------
    @staticmethod
    def can(role, permission):
        return permission in PERMISSIONS.get(role, set())

    @staticmethod
    def require(role, permission):
        if not AuthService.can(role, permission):
            raise AppError("FORBIDDEN", "Bạn không có quyền thực hiện thao tác này")
