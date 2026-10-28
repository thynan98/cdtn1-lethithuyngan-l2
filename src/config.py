import os

from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "warranty")

# Khóa ký token đăng nhập. PHẢI đặt trong .env; giá trị dưới đây chỉ để chạy thử cục bộ.
_DEV_SECRET = "chi-dung-de-chay-thu-hay-dat-JWT_SECRET-trong-env"
JWT_SECRET = os.getenv("JWT_SECRET") or _DEV_SECRET
JWT_SECRET_IS_DEFAULT = JWT_SECRET == _DEV_SECRET
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))   # 8 giờ
