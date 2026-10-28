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
