"""Điểm khởi chạy ứng dụng. Chỉ ghép các tầng, không chứa quy tắc nghiệp vụ.

Chỗ DUY NHẤT dịch mã lỗi nghiệp vụ (AppError.code) sang mã HTTP nằm ở đây.
"""
import logging
import mimetypes
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo.errors import PyMongoError

from src import config
from src.database import get_db
from src.errors import AppError
from src.logging_config import request_id_var, setup_logging
from src.routes import auth, categories, customers, overview, technicians, tickets

setup_logging()                      # cấu hình log một lần, ở điểm vào

mimetypes.add_type("application/javascript", ".js")   # Windows đôi khi khai sai loại file .js
mimetypes.add_type("text/css", ".css")
logger = logging.getLogger(__name__)

# Mã lỗi nghiệp vụ -> mã HTTP (api-contract.md)
HTTP_STATUS = {
    "REQUIRED_FIELD_MISSING": 400,
    "INVALID_FORMAT": 400,
    "UNAUTHORIZED": 401,
    "INVALID_CREDENTIALS": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INVALID_TRANSITION": 409,
    "TICKET_CLOSED": 409,
    "DUPLICATE_CODE": 409,
}


def error_body(code, message, fields=None):
    """Thân lỗi chuẩn của mọi response lỗi: {"error": {"code", "message", "fields"}}."""
    return {"error": {"code": code, "message": message, "fields": fields or {}}}


app = FastAPI(title="Hệ thống phiếu bảo hành - Mekong Mobile")

if config.JWT_SECRET_IS_DEFAULT:
    logger.warning("Chưa đặt JWT_SECRET trong .env, đang dùng khóa chạy thử.")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or request_id_var.get()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Gán mã tương quan cho mỗi yêu cầu, trả về ở header X-Request-Id và ghi một dòng log khi xong.

    Chỉ ghi đường dẫn, KHÔNG ghi query string (có thể chứa số điện thoại khách).
    """
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]
    request.state.request_id = rid
    request_id_var.set(rid)
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    logger.info("yêu cầu hoàn tất", extra={
        "method": request.method, "path": request.url.path, "status": response.status_code,
        "duration_ms": round((time.perf_counter() - start) * 1000, 1)})
    return response


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    """Lỗi người dùng (sai dữ liệu, sai quyền...): báo rõ để người dùng tự sửa được.

    Đây là nghiệp vụ bình thường nên chỉ ghi INFO, không ghi ERROR.
    """
    status = HTTP_STATUS.get(exc.code, 400)
    logger.info("vi phạm quy tắc hoặc dữ liệu không hợp lệ", extra={"error_code": exc.code, "status": status})
    return JSONResponse(error_body(exc.code, exc.message, exc.fields), status_code=status)


@app.exception_handler(RequestValidationError)
async def handle_bad_request(request: Request, exc: RequestValidationError):
    """Body không phải JSON, hoặc tham số sai kiểu (ví dụ id không phải số)."""
    fields = {str(err["loc"][-1]): "Giá trị không hợp lệ" for err in exc.errors() if err.get("loc")}
    return JSONResponse(error_body("INVALID_FORMAT", "Dữ liệu không hợp lệ", fields), status_code=400)


@app.exception_handler(PyMongoError)
async def handle_db_error(request: Request, exc: PyMongoError):
    """Lỗi hệ thống: ghi log đầy đủ để điều tra, nhưng KHÔNG lộ chi tiết kỹ thuật cho người dùng."""
    logger.error("Lỗi cơ sở dữ liệu", exc_info=exc)
    return JSONResponse(error_body(
        "DB_UNAVAILABLE",
        f"Hệ thống tạm thời không truy cập được dữ liệu. Vui lòng thử lại. Mã tra cứu: {_request_id(request)}"),
        status_code=503)


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.error("Lỗi không dự kiến", exc_info=exc)
    return JSONResponse(error_body(
        "INTERNAL_ERROR", f"Có lỗi xảy ra. Vui lòng thử lại sau. Mã tra cứu: {_request_id(request)}"),
        status_code=500)


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


for router in (auth.router, tickets.router, technicians.router,
               customers.router, categories.router, overview.router):
    app.include_router(router)

# Phục vụ giao diện (thư mục frontend/) cùng địa chỉ với API. PHẢI đặt sau cùng.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
