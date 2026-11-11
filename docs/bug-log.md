# Nhật ký lỗi (Bug Log)

Mỗi mục ghi theo 7 dòng: mã và mức độ, phát hiện bởi, triệu chứng, cách tái lập, nguyên nhân, cách sửa, commit và xác nhận.
Dòng "Nguyên nhân" ghi nguyên nhân gốc, không ghi lại triệu chứng.

## BUG-001 · Major · Chạy migrate và seed báo không kết nối được cơ sở dữ liệu

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-001 · Major: không dựng được cơ sở dữ liệu nên không chạy được hệ thống |
| 2. Phát hiện bởi | Em gặp khi chạy `python -m migrations.migrate` trên máy em sau khi chép mã mới về |
| 3. Triệu chứng | Lệnh báo lỗi `localhost:27017 connection refused`; `seed` cũng báo lỗi tương tự |
| 4. Cách tái lập | Để `MONGODB_URI=mongodb://localhost:27017` trong `.env` khi máy không chạy MongoDB cục bộ, rồi chạy `python -m migrations.migrate` |
| 5. Nguyên nhân | Tệp `.env` của em đang trỏ vào `localhost` (giá trị mẫu trong `.env.example`) trong khi em dùng MongoDB Atlas; máy em không có MongoDB chạy ở cổng 27017. Đây là lỗi cấu hình |
| 6. Cách sửa | Sửa `MONGODB_URI` trong `.env` về chuỗi kết nối Atlas. README mục 3 ghi rõ phải điền `MONGODB_URI` theo cách chạy đang dùng |
| 7. Commit và xác nhận | Không có thay đổi mã vì `.env` không đưa lên Git. Xác nhận: chạy lại `migrate` báo tạo đủ 7 collection, `seed` chạy xong, lần hai báo thêm 0 |

## BUG-002 · Minor · Máy chưa chạy được Docker

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-002 · Minor: ảnh hưởng cách chạy bằng Docker, không ảnh hưởng mã nguồn |
| 2. Phát hiện bởi | Em gặp khi chạy lệnh `docker compose up -d` lần đầu trên máy em |
| 3. Triệu chứng | PowerShell báo `docker : The term 'docker' is not recognized...`; sau khi cài Docker Desktop thì nó báo `Docker Desktop - WSL not installed` |
| 4. Cách tái lập | Chạy `docker compose up` trên máy Windows chưa cài Docker Desktop và chưa cài WSL |
| 5. Nguyên nhân | Máy em chưa cài Docker Desktop; sau khi cài thì thiếu WSL, thành phần mà Docker Desktop cần trên Windows. Đây là lỗi môi trường |
| 6. Cách sửa | Cài Docker Desktop; chạy `wsl --install` trong PowerShell quản trị, đặt tên người dùng cho Ubuntu, khởi động lại máy rồi mở lại Docker Desktop |
| 7. Commit và xác nhận | Không có thay đổi mã. Xác nhận: `docker --version` hiện phiên bản, `docker compose up --build` chạy xong và mở được http://localhost:8000 với 60 phiếu mẫu |

## BUG-003 · Major · `.gitignore` mất dòng `.env`, nguy cơ đưa chuỗi kết nối cơ sở dữ liệu lên GitHub

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-003 · Major: nguy cơ lộ chuỗi kết nối cơ sở dữ liệu |
| 2. Phát hiện bởi | Em rà lại `.gitignore` và lịch sử Git trước khi nộp |
| 3. Triệu chứng | Từ commit d991622 trở đi, `.gitignore` không còn dòng `.env`, nên tệp `.env` thật (chứa chuỗi kết nối Atlas) có thể bị `git add .` đưa lên GitHub. Chưa bị đưa lên: `git log --all --oneline -- .env` không có kết quả |
| 4. Cách tái lập | Ở commit d991622, tạo tệp `.env` rồi chạy `git status`: tệp hiện ra ở mục chưa theo dõi (`??`) |
| 5. Nguyên nhân | Ở commit d991622, em thay toàn bộ nội dung `.gitignore` bằng danh sách mới (`.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`) mà không giữ lại dòng `.env` của bản khởi tạo 8c00668. Đây là lỗi do em ghi đè file |
| 6. Cách sửa | Thêm `.env`, `data/raw/`, `*.csv` (trừ `data/sample/*.csv`) vào `.gitignore`; chỉ commit `.env.example` với giá trị giả; dùng `git add` theo từng đường dẫn thay vì `git add .` |
| 7. Commit và xác nhận | Sửa: [08f34be](https://github.com/thynan98/cdtn1-lethithuyngan-l2/commit/08f34be). Test hồi quy: `test_bug003_gitignore_chan_tep_env` trong [fab1de0](https://github.com/thynan98/cdtn1-lethithuyngan-l2/commit/fab1de0): FAIL khi xóa dòng `.env`, PASS khi có dòng này. `git log --all --oneline -- .env` không có kết quả |

## BUG-004 · Minor · Gửi form xong không thấy dòng log trong cửa sổ máy chủ

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-004 · Minor: không ảnh hưởng hệ thống, chỉ khó theo dõi log |
| 2. Phát hiện bởi | Em gặp khi kiểm tra tính năng ghi log trên máy em |
| 3. Triệu chứng | Em tạo phiếu thành công trên giao diện nhưng cửa sổ chạy `uvicorn` không hiện dòng "đã tạo phiếu" mà chỉ thấy các dòng `GET` cũ |
| 4. Cách tái lập | Bấm chuột vào cửa sổ PowerShell đang chạy máy chủ (bật chế độ chọn chữ), rồi tạo phiếu trên giao diện |
| 5. Nguyên nhân | Khi em bấm chuột vào cửa sổ PowerShell, cửa sổ chuyển sang chế độ chọn chữ (Select) và tạm dừng in; log chưa mất, chỉ bị giữ lại chưa hiện |
| 6. Cách sửa | Nhấn `Esc` (hoặc `Enter`) trong cửa sổ PowerShell để thoát chế độ chọn; các dòng log hiện ra đủ |
| 7. Commit và xác nhận | Không có thay đổi mã. Xác nhận: tạo phiếu mới thì hiện dòng log "đã tạo phiếu" kèm mã phiếu, không có số điện thoại hay tên khách |

# BẢN NHÁP: hai mục Bug Log mới và phần cập nhật Test Report

Bạn đọc, kiểm tra từng dòng với repo và ảnh, rồi viết lại bằng lời của mình.

---

## A. Dán thêm vào cuối `docs/bug-log.md` (sau BUG-004)

## BUG-005 · Critical · Khóa ký token mặc định nằm trong repo công khai, ai cũng giả được token quản lý

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-005 · Critical: ai đọc repo công khai cũng tự ký được token quản lý, xem toàn bộ dữ liệu và xóa phiếu |
| 2. Phát hiện bởi | TC-11 (test chạy tay, loại bảo mật): token em tự ký bằng khóa mặc định trong repo, gọi API trên hệ thống dựng từ bản clone mới |
| 3. Triệu chứng | Token giả vai trò QUAN_LY được chấp nhận: `GET /api/auth/me` trả 200 với `quanly01`, `GET /api/overview` trả 200 kèm số liệu 60 phiếu. Mong đợi là 401 |
| 4. Cách tái lập | Clone commit 465641a, chạy `docker compose up -d --build` (không tạo `.env`), rồi `python tools/manual_checks.py tc11` |
| 5. Nguyên nhân | `src/config.py` viết `os.getenv("JWT_SECRET") or _DEV_SECRET` và `docker-compose.yml` viết `${JWT_SECRET:-docker-chay-thu-...}`. Khi máy không có `.env`, hệ thống rơi về khóa mặc định nằm công khai trong repo. Em thiếu bước bắt buộc phải đặt khóa lúc khởi động |
| 6. Cách sửa | Bỏ khóa mặc định ở cả hai nơi. Thêm `check_jwt_secret()` trong `src/config.py`, gọi lúc khởi động trong `src/main.py`: thiếu khóa hoặc khóa dưới 32 ký tự thì app dừng. Compose dùng `${JWT_SECRET:?...}`. `.env.example` có khóa mẫu 49 ký tự kèm lệnh sinh khóa riêng |
| 7. Commit và xác nhận | Sửa: [de57a6e](https://github.com/thynan98/cdtn1-lethithuyngan-l2/commit/de57a6e). Test hồi quy (`tests/test_config.py` và ba test trong `tests/test_repo_hygiene.py`): 6 FAIL trước khi sửa, `python -m pytest -q` cho 64 passed sau khi sửa. Chạy lại TC-11 trên bản clone mới: cả hai endpoint trả 401. Khi chưa có `.env`, `docker compose up` dừng và báo thiếu JWT_SECRET. Giới hạn còn lại: khóa mẫu trong `.env.example` vẫn công khai, nên khi triển khai thật phải đổi (ghi trong Deployment Guide) |

## BUG-006 · Minor · Id quá lớn làm API trả lỗi 500 thay vì 404

| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-006 · Minor: không mất dữ liệu, không lộ thông tin; chỉ xảy ra khi gọi API với id vô lý, nhưng vi phạm hợp đồng API (phải trả 404) |
| 2. Phát hiện bởi | TC-09 (test chạy tay, loại dữ liệu sai): mở phiếu bằng id không tồn tại |
| 3. Triệu chứng | `GET /api/tickets/999999` trả 404 đúng, nhưng `GET /api/tickets/99999999999999999999` trả HTTP 500 `INTERNAL_ERROR` (mã tra cứu 76e46cfc). Mong đợi là 404 |
| 4. Cách tái lập | Hệ thống đang chạy, đăng nhập `nhanvien01`, chạy `python tools/manual_checks.py tc09` |
| 5. Nguyên nhân | MongoDB chỉ lưu số nguyên tối đa 8 byte. Id lớn hơn 9223372036854775807 làm `pymongo` ném `OverflowError` ở `find_one`. FastAPI chỉ kiểm id là số nguyên chứ không kiểm khoảng giá trị, và không có chỗ nào bắt lỗi này nên nó rơi vào `handle_unexpected` và thành 500 |
| 6. Cách sửa | Thêm hàm `is_storable_id` (id từ 1 đến 2^63-1) trong `src/repositories/id_generator.py`. Hàm `get` của kho phiếu, kỹ thuật viên và loại lỗi trả `None` khi id ngoài khoảng, nên service trả 404 như bình thường |
| 7. Commit và xác nhận | Sửa: [18634b2](https://github.com/thynan98/cdtn1-lethithuyngan-l2/commit/18634b2). Test hồi quy `tests/test_id_range.py` (4 test): 3 FAIL trước khi sửa, 68 passed sau khi sửa. Chạy lại TC-09 trên bản clone mới: cả hai id trả 404 |

---

## B. Sửa `docs/test-report.md`

Đoạn đầu: đổi thành

> Lần chạy đầu (11/11/2026): 12 test case, 10 PASS, 2 FAIL (TC-09, TC-11). Sau khi sửa BUG-005 và BUG-006, em chạy lại: 12/12 PASS. Bộ test tự động `python -m pytest -q` cho 68 passed.

Hai dòng P/F của bảng:

- TC-09: `FAIL lần đầu (BUG-006); chạy lại sau sửa: PASS (cả hai id trả 404)`
- TC-11: `FAIL lần đầu (BUG-005); chạy lại sau sửa: PASS (cả hai endpoint trả 401)`

Phần "Ghi chú về tính trung thực" thay phần "(Phần 'Sau khi sửa' em sẽ điền sau...)" bằng:

> Ảnh lúc FAIL giữ nguyên là `TC-09.png` và `TC-11.png`; ảnh chạy lại sau sửa là `TC-09-sau-sua.png` và `TC-11-sau-sua.png`. Ảnh test hồi quy: `BUG-005-truoc-sua.png`, `BUG-005-sau-sua.png`, `BUG-006-truoc-sua.png`, `BUG-006-sau-sua.png`.