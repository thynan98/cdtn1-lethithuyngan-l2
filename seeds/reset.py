"""Xóa SẠCH dữ liệu của ứng dụng để chạy lại migration và seed từ trạng thái trống.

Chạy:  python -m seeds.reset --yes
Không có --yes thì chỉ in cảnh báo, không xóa gì. Chỉ dùng trên cơ sở dữ liệu thử nghiệm.
"""
import sys

from migrations.migrate import COLLECTIONS
from src import config
from src.database import get_db

if __name__ == "__main__":
    db = get_db()
    names = list(COLLECTIONS) + ["counters"]
    if "--yes" not in sys.argv:
        print(f"Sẽ xóa {len(names)} collection trong cơ sở dữ liệu '{config.MONGODB_DB}'. "
              "Chạy lại với --yes để xác nhận.")
        sys.exit(1)
    for name in names:
        db.drop_collection(name)
    print(f"Đã xóa {len(names)} collection trong '{config.MONGODB_DB}'.")
