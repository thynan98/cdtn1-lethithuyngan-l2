# Test Report - Luồng L2: Yêu cầu bảo hành

Lần chạy đầu (11/11/2026): 12 test case, **10 PASS, 2 FAIL** (TC-09, TC-11).
Sau khi sửa BUG-005 và BUG-006, em chạy lại hai test case này: **12/12 PASS**.
Bộ test tự động: `python -m pytest -q` cho **68 passed**, 1 cảnh báo của thư viện
(StarletteDeprecationWarning về `httpx`, không liên quan mã của em).
TC-09, TC-11, TC-12 và lần chạy tay của TC-10 chạy trên hệ thống dựng bằng Docker từ
bản clone mới của repo (`git clone` rồi `docker compose up -d --build`).
Ảnh chụp từng test case nằm trong [docs/screenshots/](screenshots/).

| Mã | Tiền điều kiện | Các bước | Dữ liệu thử | Kết quả mong đợi | Ưu tiên | Kết quả thực tế | P/F |
|---|---|---|---|---|---|---|---|
| TC-01 | Không cần cơ sở dữ liệu | Chạy `test_tc01_happy_due_date_medium_priority` | Nhận phiếu lúc 14:30 thứ Hai 05/10/2026, mức TRUNG_BINH | Hạn cam kết là 14:30 thứ Năm 08/10/2026 (+3 ngày làm việc) | Cao | Trả về đúng 08/10/2026 14:30; pytest báo `1 passed` | PASS |
| TC-02 | Không | Chạy `test_tc04_happy_status_moves_one_way` | MOI sang DANG_XU_LY, rồi DANG_XU_LY sang HOAN_TAT | Cả hai lần chuyển đều được chấp nhận, không ném lỗi | Cao | Không ném lỗi; `1 passed` | PASS |
| TC-03 | Không | Chạy `test_tc07_happy_phone_normalized_to_10_digits` | `+84 912.345 678` và `84912345678` | Cả hai thành `0912345678` | Cao | Cả hai ra `0912345678`; `1 passed` | PASS |
| TC-04 | Không | Chạy `test_tc02_boundary_saturday_high_priority_skips_sunday` | Nhận phiếu lúc 14:30 thứ Bảy 10/10/2026, mức CAO | Hạn là thứ Hai 12/10/2026 (bỏ qua Chủ nhật) | Cao | Trả về 12/10/2026 14:30; `1 passed` | PASS |
| TC-05 | Không | Chạy `test_tc08_boundary_description_exactly_10_chars_is_accepted` | Mô tả lỗi đúng 10 ký tự `1234567890` | Được chấp nhận, mức ưu tiên mặc định TRUNG_BINH | Cao | Được chấp nhận, priority = TRUNG_BINH; `1 passed` | PASS |
| TC-06 | Không | Chạy `test_boundary_description_9_chars_is_rejected` | Mô tả lỗi 9 ký tự `123456789` | Bị từ chối, mã `INVALID_FORMAT`, nêu trường `issue_desc` | Cao | Ném `INVALID_FORMAT`, danh sách trường có `issue_desc`; `1 passed` | PASS |
| TC-07 | Không | Chạy `test_tc05_invalid_status_cannot_skip_step` | Chuyển thẳng MOI sang HOAN_TAT | Bị từ chối, mã `INVALID_TRANSITION` | Cao | Ném `INVALID_TRANSITION`; `1 passed` | PASS |
| TC-08 | Không | Chạy `test_tc06_invalid_missing_phone_returns_field_name` | Tạo phiếu thiếu số điện thoại | Bị từ chối, mã `REQUIRED_FIELD_MISSING`, nêu `customer_phone` | Cao | Ném `REQUIRED_FIELD_MISSING`, có `customer_phone`; `1 passed` | PASS |
| TC-09 | Hệ thống chạy bằng Docker, đã nạp dữ liệu mẫu; đăng nhập `nhanvien01` | `GET /api/tickets/{id}` với hai id không tồn tại (script `tools/manual_checks.py tc09`) | `999999` và `99999999999999999999` | Cả hai trả HTTP 404 `NOT_FOUND` | Trung bình | Lần đầu: id `999999` trả 404 đúng, id `99999999999999999999` trả **HTTP 500** `INTERNAL_ERROR` (mã tra cứu 76e46cfc). Sau khi sửa BUG-006: cả hai id trả 404 | **FAIL lần đầu** (BUG-006); chạy lại sau sửa: **PASS** |
| TC-10 | Hệ thống chạy như TC-09; đăng nhập `quanly01` | `POST /api/tickets` bằng tài khoản quản lý. Chạy thêm test tự động `test_manager_cannot_create_ticket` | Thân phiếu hợp lệ: tên An, số `0912345678`, mô tả 21 ký tự | HTTP 403 `FORBIDDEN`, phiếu không được tạo | Cao | Chạy tay: 403 `FORBIDDEN`. Test tự động: `1 passed` | PASS |
| TC-11 | Hệ thống dựng từ bản clone mới, không có file `.env` | Tự ký một token vai trò QUAN_LY bằng khóa mặc định ghi trong `docker-compose.yml`, rồi gọi `GET /api/auth/me` và `GET /api/overview` | Token giả cho `quanly01`, hạn 1 giờ | HTTP 401 `UNAUTHORIZED` (hệ thống chỉ được nhận token do chính nó cấp) | Cao | Lần đầu: cả hai trả **HTTP 200** (`/api/auth/me` trả `quanly01`, `QUAN_LY`; `/api/overview` trả đủ số liệu, tổng 60 phiếu). Sau khi sửa BUG-005: cả hai trả 401 | **FAIL lần đầu** (BUG-005); chạy lại sau sửa: **PASS** |
| TC-12 | Hệ thống đã chạy và đã nạp dữ liệu mẫu lần đầu | `docker compose exec app python -m seeds.seed` (lần hai) | Dữ liệu mẫu trong `data/sample` | Mỗi collection báo `thêm 0`, số bản ghi không đổi | Cao | Cả 5 dòng `thêm 0`; hiện có 6 loại lỗi, 38 kỹ thuật viên, 2 tài khoản, 60 khách, 60 phiếu | PASS |

## Ghi chú về tính trung thực

TC-09 và TC-11 **FAIL ở lần chạy đầu** và em giữ nguyên ảnh chụp lúc FAIL
(`TC-09.png`, `TC-11.png`). Hai lỗi được ghi ở `docs/bug-log.md` (BUG-006 và BUG-005).
Sau khi sửa, em chạy lại trên bản clone mới và chụp ảnh `TC-09-sau-sua.png`,
`TC-11-sau-sua.png`. Ảnh chạy test hồi quy: `BUG-005-truoc-sua.png`,
`BUG-005-sau-sua.png`, `BUG-006-truoc-sua.png`, `BUG-006-sau-sua.png`.
Khi chưa có file `.env`, `docker compose up` dừng và báo thiếu JWT_SECRET
(ảnh `BUG-005-compose-thieu-khoa.png`).