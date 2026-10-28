"""Cấu hình log MỘT lần ở điểm vào (src/main.py). Các module khác chỉ dùng logging.getLogger(__name__).

Mỗi dòng log là một đối tượng JSON ghi ra stdout, có 3 thứ: thời điểm (có múi giờ),
ngữ cảnh (request_id) và mô tả chuyện gì xảy ra. TUYỆT ĐỐI không ghi mật khẩu, token,
chuỗi kết nối, số điện thoại: chỉ ghi ID (ticket_id, user_id).
"""
import contextvars
import json
import logging
import os
import sys

from src.timeutil import now_vn

# Mã tương quan của yêu cầu đang xử lý; middleware trong main.py gán cho từng yêu cầu
request_id_var = contextvars.ContextVar("request_id", default="-")

# Trường ngữ cảnh được phép đi kèm dòng log (khai báo trước, trường lạ bị bỏ qua)
CONTEXT_FIELDS = ("ticket_id", "user_id", "method", "path", "status", "duration_ms", "error_code")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "thoi_diem": now_vn().isoformat(timespec="seconds"),
            "muc": record.levelname,
            "nguon": record.name,
            "request_id": request_id_var.get(),
            "thong_diep": record.getMessage(),
        }
        for key in CONTEXT_FIELDS:
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        if record.exc_info:
            entry["loi"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def setup_logging():
    """Gọi đúng một lần khi khởi động. Mức log lấy từ biến môi trường LOG_LEVEL."""
    handler = logging.StreamHandler(sys.stdout)          # stdout, không ghi tệp
    handler.setFormatter(JsonFormatter())
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("uvicorn.access").disabled = True  # tránh trùng với dòng "yêu cầu hoàn tất" của ta
