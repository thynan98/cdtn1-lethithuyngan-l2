# Checklist bảo mật - Luồng L2: Yêu cầu bảo hành

Em tự kiểm bảy mục bằng cách chạy lệnh thật trên hệ thống đang chạy bằng Docker (ngày 11/11/2026).
Mỗi mục có một trạng thái và một dòng minh chứng; ảnh chụp nằm trong `docs/screenshots/`.

## 1. Không có secret nào trong repo — ĐÃ LÀM

Minh chứng: `git log --all --oneline -- .env` cho kết quả rỗng (file `.env` chưa từng được commit); `git log -p --all | Select-String "mongodb\+srv://...@...mongodb.net"` rỗng (không có chuỗi kết nối Atlas thật trong lịch sử).
Ảnh: `docs/screenshots/sec-1.png`

Ghi chú trung thực: khóa `JWT_SECRET` trong `.env.example` chỉ là khóa mẫu và công khai, đã ghi rõ trong Deployment Guide là phải đổi khi dùng thật. File `tools/manual_checks.py` có chứa khóa mặc định cũ dùng để giả token ở TC-11; khóa đó đã bị loại khỏi hệ thống từ khi sửa BUG-005 nên không còn dùng được.

## 2. Dữ liệu vào được kiểm ở tầng ứng dụng — ĐÃ LÀM

Minh chứng: ba lệnh grep tìm ghép chuỗi vào truy vấn (`$where`, `eval`), `innerHTML` và `exec`/`subprocess` đều không thấy chỗ nguy hiểm (chỉ ra một dòng chú thích trong `dom.js` nói rằng giao diện không dùng `innerHTML`). Gửi `{"$ne":null}` làm tên đăng nhập trả 401 `INVALID_CREDENTIALS`, không có token, vì `auth_service.py` ép giá trị về chuỗi trước khi tra cứu. Test dữ liệu sai TC-06 và TC-08 đều PASS.
Ảnh: `docs/screenshots/sec-2-grep.png`, `docs/screenshots/sec-2-injection.png`

## 3. Kiểm soát truy cập — ĐÃ LÀM (theo vai trò); KHÔNG ÁP DỤNG theo chủ sở hữu

Minh chứng: tài khoản quản lý gửi `POST /api/tickets` bị trả 403 `FORBIDDEN` và phiếu không được tạo (TC-10, có thêm test tự động `test_manager_cannot_create_ticket`). Bảng quyền hai vai trò nằm trong `PERMISSIONS` ở `src/services/auth_service.py`.
Ảnh: `docs/screenshots/TC-10-manual.png`

Lý do không áp dụng theo chủ sở hữu: hệ thống chỉ có tài khoản nhân viên và quản lý, khách hàng không đăng nhập nên không có chuyện "khách A sửa phiếu của khách B".

## 4. Mật khẩu được băm — ĐÃ LÀM

Minh chứng: `db.user.find({}, {username:1, password_hash:1})` trong MongoDB cho `password_hash` dạng `pbkdf2_sha256$200000$<muối>$<băm>`: PBKDF2-SHA256, 200.000 vòng, mỗi tài khoản có muối riêng, không đọc ngược ra mật khẩu. (Em dùng PBKDF2 chứ không phải bcrypt như ví dụ trong bài giảng.)
Ảnh: `docs/screenshots/sec-4.png`

## 5. Thông báo lỗi không lộ cấu trúc trong — ĐÃ LÀM

Minh chứng: gửi JSON hỏng cho `/api/auth/login` trả 400 `INVALID_FORMAT` với thông báo ngắn; tắt MongoDB rồi đăng nhập trả 503 `DB_UNAVAILABLE` kèm mã tra cứu. Cả hai phản hồi không có stack trace, tên tệp, tên collection hay chuỗi kết nối.
Ảnh: `docs/screenshots/sec-5-json-hong.png`, `docs/screenshots/sec-5-db-tat.png`

## 6. Nhật ký không ghi secret hay dữ liệu cá nhân — ĐÃ LÀM

Minh chứng: `docker compose logs app | Select-String "password|token|0[0-9]{9}|NhanVien@|QuanLy@"` không ra dòng nào, trong khi log đã ghi các lần gọi `/api/auth/login` (401, 400, 503). Mỗi dòng log chỉ có thời điểm, mức, `request_id`, method, path, status và thời gian xử lý.
Ảnh: `docs/screenshots/sec-6.png`

## 7. Phụ thuộc ghim phiên bản, đã kiểm lỗ hổng — ĐÃ LÀM

Minh chứng: `requirements.txt` ghim phiên bản (`==`) cho cả 27 gói; `pip-audit -r requirements.txt` báo "No known vulnerabilities found" (chạy ngày 11/11/2026).
Ảnh: `docs/screenshots/sec-7.png`

Ghi chú trung thực: kết quả chỉ đúng với cơ sở dữ liệu lỗ hổng tại ngày chạy. Gói kiểm thử (`pytest`) nằm chung trong `requirements.txt`, em chưa tách riêng gói chỉ dùng khi phát triển.

## Giới hạn còn lại

- Khóa `JWT_SECRET` mẫu trong `.env.example` là công khai, khi triển khai thật phải sinh khóa riêng.
- Hệ thống phục vụ bằng HTTP, chưa có HTTPS; khi triển khai thật cần đặt sau một reverse proxy có chứng chỉ.