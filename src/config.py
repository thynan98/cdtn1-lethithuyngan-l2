import os

from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "warranty")
# Khóa ký token đăng nhập. PHẢI đặt trong .env (hoặc biến môi trường); repo không giữ giá trị mặc định
# nào, vì repo công khai: ai đọc được khóa là tự ký được token quản lý (BUG-005).
MIN_JWT_SECRET_LENGTH = 32
JWT_SECRET = os.getenv("JWT_SECRET", "")


def check_jwt_secret(secret=None):
    """Dừng ngay lúc khởi động nếu thiếu khóa ký token hoặc khóa quá ngắn."""
    secret = JWT_SECRET if secret is None else secret
    if len(secret) < MIN_JWT_SECRET_LENGTH:
        raise RuntimeError(
            f"Thiếu JWT_SECRET hoặc quá ngắn (cần ít nhất {MIN_JWT_SECRET_LENGTH} ký tự). "
            "Sao chép .env.example thành .env rồi đặt JWT_SECRET.")

    
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))   # 8 giờ
