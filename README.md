# Hệ thống tiếp nhận và theo dõi phiếu bảo hành của trung tâm Mekong Mobile (luồng L2)

Sinh viên: Lê Thị Thùy Ngân - 2374802010328 - Track SE

Học phần: Chuyên đề Tốt nghiệp 1, HK1 2026-2027

Luồng nghiệp vụ: L2 – Yêu cầu bảo hành (service desk)

## 1. Mục tiêu

Tại trung tâm bảo hành Mekong Mobile, yêu cầu bảo hành đang được ghi trên phiếu giấy nên khó biết phiếu đang ở bước nào, ai đang xử lý và đã quá hạn cam kết với khách hay chưa. Hệ thống này giúp nhân viên tiếp nhận ghi nhận yêu cầu thành phiếu, phân loại theo loại lỗi, gán kỹ thuật viên và theo dõi trạng thái từ lúc tiếp nhận đến khi hoàn tất. Hệ thống tính hạn cam kết theo mức ưu tiên và cảnh báo phiếu sắp hoặc đã quá hạn, để nhân viên và quản lý trung tâm biết phiếu nào cần xử lý hoặc can thiệp.

## 2. Yêu cầu môi trường

Chọn một trong hai cách chạy ở mục 3.

- Cách 1 (Docker): chỉ cần Git và Docker Desktop.
- Cách 2 (Python): Python 3.11 trở lên (đã chạy thử trên Python 3.14.2, Windows), Git, và một MongoDB (cài trên máy tại `localhost:27017`, hoặc MongoDB Atlas).
- Trình duyệt web hiện đại (giao diện HTML/CSS/JavaScript).
- Biến môi trường (chỉ cần ở cách 2): xem `.env.example` gồm `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `LOG_LEVEL`.

## 3. Hướng dẫn chạy

Lấy mã nguồn (cả hai cách):

1. `git clone --branch v0.2 https://github.com/thynan98/cdtn1-lethithuyngan-l2.git`
2. `cd cdtn1-lethithuyngan-l2`

### Cách 1: chạy bằng Docker (một lệnh)

3. Mở Docker Desktop và chờ đến khi báo "Engine running".
4. `docker compose up --build`
5. Chờ đến khi thấy dòng `Uvicorn running on http://0.0.0.0:8000`, rồi mở http://localhost:8000.

Hệ thống tự dựng collection và nạp dữ liệu mẫu. Dừng bằng `Ctrl + C`, sau đó `docker compose down`.

### Cách 2: chạy trực tiếp bằng Python

Các lệnh viết cho Windows PowerShell; macOS/Linux đổi lệnh ở bước 4 và 6 như ghi chú.

3. `python -m venv .venv`
4. `.venv\Scripts\Activate.ps1`  (macOS/Linux: `source .venv/bin/activate`)
   Nếu PowerShell báo không cho chạy script, chạy `Set-ExecutionPolicy -Scope Process Bypass` rồi thử lại.
5. `pip install -r requirements.txt`
6. `Copy-Item .env.example .env`  (macOS/Linux: `cp .env.example .env`)
   Mở `.env` và điền `MONGODB_URI` (MongoDB trên máy: `mongodb://localhost:27017`; hoặc chuỗi kết nối Atlas) và `JWT_SECRET` (một chuỗi ngẫu nhiên dài ít nhất 32 ký tự). KHÔNG commit file `.env`.
7. `python -m migrations.migrate`  (tạo 7 collection và chỉ mục; chạy lại không lỗi)
8. `python -m seeds.seed`  (nạp dữ liệu mẫu; chạy lại nhiều lần vẫn không nhân đôi dữ liệu)
9. `uvicorn src.main:app --port 8000`
10. Mở http://127.0.0.1:8000 (giao diện) hoặc http://127.0.0.1:8000/docs (thử API).

### Tài khoản chạy thử

- `nhanvien01` / `NhanVien@2026` (nhân viên tiếp nhận)
- `quanly01` / `QuanLy@2026` (quản lý trung tâm)

## 4. Cấu trúc thư mục

- `src/routes` (cổng HTTP) -> `src/services` (nghiệp vụ) -> `src/repositories` (đọc/ghi MongoDB); `src/services` gọi `src/validators` để kiểm tra dữ liệu vào
- `migrations/` dựng collection; `seeds/` nạp dữ liệu mẫu; `tests/` kiểm thử; `frontend/` giao diện; `data/sample/` dữ liệu mẫu; `docs/` tài liệu.
- `Dockerfile`, `docker-compose.yml`: đóng gói để chạy bằng Docker.

## 5. Kiểm thử

`python -m pytest -q` - chạy toàn bộ test bằng một lệnh. Không cần MongoDB vì dùng kho dữ liệu giả (`tests/fakes.py`), nên kết quả không phụ thuộc dữ liệu trên máy. Hiện có 57 test, gồm đủ ba loại: luồng đúng, giá trị biên và dữ liệu sai. Trong đó có 2 test hồi quy cho BUG-003 (`tests/test_repo_hygiene.py`).

## 6. Dữ liệu mẫu

Dữ liệu mẫu là bộ dữ liệu mô phỏng của case study Mekong Mobile do giảng viên cung cấp.

- Bản mẫu nhỏ có sẵn trong `data/sample/` (38 kỹ thuật viên, 6 loại lỗi, 60 phiếu cùng khách hàng và nhật ký trạng thái) và được `python -m seeds.seed` nạp vào cơ sở dữ liệu.
- Bộ đầy đủ không đưa lên Git. Nếu cần, đặt vào `data/raw/` rồi chạy `python tools/make_sample.py` để tạo lại bản mẫu.
- Dựng lại từ cơ sở dữ liệu trống: `python -m seeds.reset --yes`, sau đó chạy lại `migrations.migrate` và `seeds.seed`. Chỉ dùng trên cơ sở dữ liệu thử nghiệm.

## 7. Tài liệu

- `docs/thay-doi-thiet-ke.md`: các thay đổi so với thiết kế BT1 (TD-01 đến TD-13)
- `docs/bug-log.md`: nhật ký lỗi đã gặp và cách gỡ (BUG-001 đến BUG-004)
- `docs/ai-disclosure.md`: khai báo sử dụng công cụ AI
- `docs/srs.md`, `docs/api-contract.md`, `docs/data-model.md`: yêu cầu, đặc tả API, mô hình dữ liệu
- `docs/architecture-thuc-te.drawio`: sơ đồ kiến trúc đã hiện thực

## 8. Trạng thái hiện tại (Bài tập 2, tag v0.2)

- [x] Tài liệu phân tích và thiết kế BT1 (SRS, use case, kiến trúc, ERD, wireframe, API contract) trong `docs/`
- [x] Tạo phiếu bảo hành (US1), phân loại phiếu (US2), gán kỹ thuật viên (US3), cập nhật trạng thái (US4)
- [x] Xem hạn cam kết, xem và lọc danh sách phiếu, xem chi tiết phiếu, tra cứu khách hàng (US5, US6, US7)
- [x] Đăng nhập và phân quyền hai vai trò, màn Tổng quan, xóa mềm phiếu (phần mở rộng, xem `docs/thay-doi-thiet-ke.md`)
- [x] Migration và seed chạy lại không nhân đôi dữ liệu
- [x] Giao diện năm màn, mỗi màn có trạng thái đang tải, rỗng, lỗi (có nút Thử lại)
- [x] Ghi log JSON và mã tra cứu khi có lỗi
- [x] Kiểm thử tự động (57 test)
- [x] Đóng gói Docker (`docker compose up --build`)
