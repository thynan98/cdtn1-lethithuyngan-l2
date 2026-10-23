"""Điểm khởi chạy ứng dụng. Chỉ ghép các tầng, không chứa quy tắc nghiệp vụ."""
import logging

from fastapi import FastAPI

from src.database import get_db

logger = logging.getLogger(__name__)

app = FastAPI(title="Hệ thống phiếu bảo hành - Mekong Mobile")


@app.get("/health")
def health():
    """Kiểm tra ứng dụng và kết nối MongoDB còn sống không."""
    try:
        get_db().command("ping")
        return {"status": "ok", "db": "ok"}
    except Exception:
        # Ghi log đầy đủ để điều tra, nhưng không lộ chi tiết kỹ thuật cho người gọi
        logger.warning("Không kết nối được MongoDB", exc_info=True)
        return {"status": "ok", "db": "unreachable"}
