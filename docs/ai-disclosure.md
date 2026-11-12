# Bảng khai báo sử dụng công cụ AI

## 1. Công cụ AI đã dùng

- **Claude** (Anthropic): ở cả BT1, BT2 và BT3.
- **Google Gemini** (phần trả lời AI khi tìm trên Google): ở BT1, để hiểu các khái niệm trong tệp API.
- **Google Stitch** (BT1) và **Figma AI** (BT2): tạo bản nháp giao diện. Em không dùng mã do Figma sinh ra.

## 2. Bảng khai báo

Bốn cột: công cụ · dùng vào việc gì · áp dụng ở tệp hoặc hàm nào · em đã kiểm chứng thế nào.
Bảng này gộp cả ba bài tập (BT1, BT2, BT3) để thầy xem được toàn bộ quá trình làm bài.

| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
|---|---|---|---|
| Claude | **BT3.** Soạn nháp bản sửa cho hai lỗi em gặp khi chạy test chạy tay: BUG-005 (bỏ khóa JWT mặc định, bắt buộc đặt `JWT_SECRET`) và BUG-006 (id quá lớn làm API trả 500 thay vì 404) | `src/config.py` (hàm `check_jwt_secret`), `src/main.py` (hàm `lifespan`), `docker-compose.yml` (biến `JWT_SECRET`), `.env.example`; `src/repositories/id_generator.py` (hàm `is_storable_id`) và hàm `get` trong `ticket_repository.py`, `technician_repository.py`, `category_repository.py` | Em chạy test chạy tay TC-11 và TC-09, thấy FAIL; sửa xong chạy lại thì PASS (ảnh `TC-11-sau-sua.png`, `TC-09-sau-sua.png`). Em tự gõ code vào tệp và tự sửa lỗi thụt dòng em gõ sai trong `ticket_repository.py`. Em chạy `python -m pytest -q` và thấy số test đi từ 58 lên 64 rồi 68 passed. Mỗi lỗi có một commit riêng (`de57a6e`, `18634b2`) |
| Claude | **BT3.** Soạn nháp các test hồi quy cho BUG-005 và BUG-006 (viết test trước, thấy FAIL, rồi mới sửa mã) | `tests/test_config.py`, `tests/test_id_range.py`, ba test thêm vào `tests/test_repo_hygiene.py`, test `test_boundary_description_9_chars_is_rejected` trong `tests/test_ticket_rules.py` | Em chạy `pytest` trước khi sửa mã: 6 test FAILED (BUG-005) và 3 test FAILED (BUG-006). Sau khi sửa mã thì tất cả passed. Em chụp ảnh trước và sau (`BUG-005-truoc-sua.png`, `BUG-005-sau-sua.png`, `BUG-006-truoc-sua.png`, `BUG-006-sau-sua.png`) |
| Claude | **BT3.** Soạn nháp hai script: `manual_checks.py` chạy các test chạy tay (giả token bằng khóa mặc định cũ, gọi API với id không tồn tại, gọi bằng tài khoản quản lý) và `api_samples.py` ghi lại phản hồi thật của 17 endpoint | `tools/manual_checks.py` (lệnh `tc09`, `tc10`, `tc11`), `tools/api_samples.py` | Em tự chạy cả hai script trên hệ thống chạy bằng Docker. Bản nháp `api_samples.py` in token ra tệp kết quả trước khi che token; em phát hiện khi đọc tệp kết quả, đã thêm đoạn che token, xóa tệp kết quả và không commit nó |
| Claude | **BT3.** Soạn nháp Test Plan, Test Report và hai mục BUG-005, BUG-006 của Bug Log | `docs/test-plan.md`, `docs/test-report.md`, `docs/bug-log.md` | Em viết lại bằng lời của mình. Em đối chiếu từng test case với tên hàm test thật trong `tests/`, ghi kết quả "FAIL lần đầu, PASS sau khi sửa" đúng với các lần chạy, và mở thử từng link commit |
| Claude | **BT3.** Soạn nháp khối `healthcheck` của dịch vụ `app` và hướng dẫn xử lý các lỗi Docker (cổng 8000 bị chiếm, lỗi phân giải tên `mongo`) | `docker-compose.yml` (khối `healthcheck` của `app`), `docs/deployment-guide.md` (mục Troubleshooting) | Em chạy `docker compose config --quiet`, `docker compose up -d --build` và `docker compose ps`, thấy cả `mongo` và `app` báo `healthy` (ảnh `docker-compose-ps-healthy.png`). Hai lỗi Docker trong Troubleshooting là lỗi em gặp thật khi chạy |
| Claude | **BT3.** Soạn nháp Deployment Guide tiếng Anh và mục bật HTTPS | `docs/deployment-guide.md` | Em đối chiếu bảng biến môi trường với `.env.example` và `src/config.py`, đối chiếu quyền hai vai trò với bảng `PERMISSIONS` trong `src/services/auth_service.py`, và chép kết quả `/health` thật. Bản nháp đầu ghi quản lý chỉ có quyền xem; em nhắc lại là quản lý còn ẩn phiếu và quản lý kỹ thuật viên, rồi hai bên đối chiếu với mã và sửa lại. Mục HTTPS em chưa triển khai thử và đã ghi rõ trong tài liệu |
| Claude | **BT3.** Gợi ý cách tự kiểm bảy mục checklist bảo mật (lệnh `git log`, grep, thử gửi dữ liệu sai, `pip-audit`) và soạn nháp checklist | `docs/checklist-bao-mat.md` | Em tự chạy từng lệnh và chụp ảnh `sec-1` đến `sec-7`. Khi thử gửi `{"$ne":null}`, kết quả thật là 401 chứ không phải 400 như dự đoán ban đầu; em đọc `src/services/auth_service.py` để hiểu lý do (giá trị được ép về chuỗi) rồi ghi đúng kết quả thật. Em ghi rõ mật khẩu được băm bằng PBKDF2 chứ không phải bcrypt như ví dụ trong bài giảng |
| Claude | **BT3.** Soạn nháp tài liệu API cho 17 endpoint theo bảy mục của đề | `docs/api-docs.md` | Phản hồi trong tài liệu chép từ lần chạy thật của `tools/api_samples.py`. Em đối chiếu quyền và mã lỗi của từng endpoint với `src/routes/` và `src/services/`, và ghi vào mục lưu ý rằng `/health` vẫn trả 200 khi MongoDB tắt |
| Claude | **BT3.** Hướng dẫn từng lệnh PowerShell, Git, Docker và cách chụp, lưu ảnh minh chứng | `docs/screenshots/` | Em tự gõ lệnh, tự chụp và lưu ảnh, chạy `git status` trước mỗi commit để chắc không có `.env`, và kiểm tra `git log` sau mỗi lần đẩy lên GitHub |
| Claude | **BT3.** Hướng dẫn các bước triển khai thử trên Render và MongoDB Atlas (tạo dịch vụ web, đặt biến môi trường, mở kết nối Atlas), tìm nguyên nhân lỗi và soạn nháp mục "Deploying to a free platform" | `docs/deployment-guide.md` (mục Deploying to a free platform), `README.md` (mục 8) | Em tự tạo dịch vụ trên Render và tự nhập biến môi trường (không ghi secret vào repo). Lần deploy đầu lỗi `bad auth : authentication failed` ở log; em sửa lại mật khẩu và chuỗi kết nối rồi deploy lại. Em kiểm bằng `/health` trả `{"status":"ok","db":"ok"}` và đăng nhập thấy 60 phiếu (ảnh `deploy-render-health.png`, `deploy-render-dang-nhap.png`) |
| Claude | **BT2.** Soạn nháp phần lớn mã nguồn backend theo thiết kế BT1: routes, validators, services, repositories, migration, seed | `src/routes/`, `src/validators/`, `src/services/`, `src/repositories/`, `migrations/`, `seeds/seed.py` | Em đọc từng phần, hỏi lại chỗ chưa hiểu, chạy trên máy mình và chỉnh theo thiết kế, rồi ghi các thay đổi vào `docs/thay-doi-thiet-ke.md`. Em chạy migrate và seed hai lần để thấy dữ liệu không bị nhân đôi, và thử bằng giao diện với hai tài khoản |
| Claude | **BT2.** Soạn nháp bộ test (luồng đúng, giá trị biên, dữ liệu sai) và test hồi quy cho BUG-003 | `tests/` (chủ yếu `tests/test_ticket_rules.py`, `tests/test_api.py`, `tests/test_repo_hygiene.py`) | Em chạy `python -m pytest -q` và đối chiếu từng test với quy tắc trong SRS mục 2.4. Em tạm xóa dòng `.env` trong `.gitignore` để thấy test FAILED, rồi khôi phục để thấy PASSED |
| Claude | **BT2.** Soạn nháp phần ghi log JSON, mã tra cứu lỗi, Docker và dữ liệu mẫu | `src/logging_config.py`, middleware trong `src/main.py`, `Dockerfile`, `docker-compose.yml`, `seeds/seed.py`, `tools/make_sample.py` | Em tạo lỗi thật (làm mất kết nối cơ sở dữ liệu) và đối chiếu mã tra cứu trên màn hình với dòng log. Em chạy seed lần hai thấy báo "thêm 0", rồi chạy `docker compose up --build` và đăng nhập xem dữ liệu |
| Claude, Figma AI | **BT2.** Figma AI, dựa trên các màn Stitch của BT1, tạo bản nháp giao diện sinh động hơn và các màn còn thiếu (như Đăng nhập). Claude soạn nháp mã HTML, CSS, JavaScript theo wireframe BT1 và thiết kế trên Figma | `frontend/` (năm màn) | Em tự viết phần mô tả trên Figma, chọn và chỉnh bản nháp; em không dùng mã do Figma sinh ra. Em chạy giao diện, thử ba trạng thái (đang tải, rỗng, lỗi) và thử bằng hai tài khoản |
| Claude | **BT2.** Hướng dẫn cài Docker và WSL, cấu hình MongoDB Atlas, tìm nguyên nhân các lỗi khi chạy và gợi ý cách chia commit | `docs/bug-log.md` (BUG-001 đến BUG-004), `README.md`, lịch sử commit | Em làm theo từng bước, chạy lại sau mỗi lần sửa, ghi các lỗi đã gặp vào Bug Log và xem lịch sử commit trên GitHub |
| Claude, Google Stitch, Google Gemini | **BT1.** Claude gợi ý cấu trúc, rà soát câu chữ và đối chiếu giữa SRS, use case, API, ERD, wireframe. Stitch tạo bản nháp 3 màn hình wireframe. Gemini giải thích các khái niệm trong tệp API | `docs/srs.md`, `docs/api-contract.md`, `docs/data-model.md`, `docs/usecase.drawio`, `docs/architecture.drawio`, `docs/erd.drawio`, `docs/wireframe.png` | Em chọn phạm vi và viết lại các câu; em tự vẽ use case, kiến trúc và ERD trên draw.io; em chọn 3 màn wireframe và viết bảng ghi chú. Em đối chiếu từng mục với case study, bảng truy vết trong SRS, và tên bảng, tên trường giữa API và ERD |

**Cam kết:** Em xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Họ tên: Lê Thị Thùy Ngân  ·  MSSV: 2374802010328  ·  Ngày: 12/11/2026

## 3. Những phần không dùng AI

- Chọn phạm vi, đề ra User Story, độ ưu tiên MoSCoW và các quy tắc nghiệp vụ trong SRS.
- Sơ đồ use case: sinh viên tự vẽ trên draw.io, tự nối actor với use case và viết đặc tả.
- Sơ đồ kiến trúc và ERD: sinh viên vẽ và chỉnh trên draw.io (bố cục, ký hiệu quan hệ, ghi chú), và tự viết các câu giải thích lựa chọn kiến trúc.
- Chọn công nghệ (Python FastAPI, MongoDB đã được giảng viên đồng ý) và các đánh đổi.
- Chọn 3 màn wireframe và viết bảng ghi chú.
- Ở BT2: tự viết phần mô tả (câu lệnh) trên Figma để thêm màu, chỉnh menu và bổ sung các màn còn thiếu; mã giao diện không lấy từ Figma.
- Đọc lại, chỉnh sửa và đối chiếu các tài liệu với nhau cho khớp.
- Ở BT2: tự chạy, thử và kiểm tra hệ thống (pytest, migrate, seed, giao diện, Docker), tự tạo lỗi thật để chụp ba trạng thái, tự vẽ lại sơ đồ kiến trúc thực tế, tự quyết định các thay đổi thiết kế và ghi vào `thay-doi-thiet-ke.md`, tự commit và đẩy lên GitHub.

- Ở BT3: chọn và chạy toàn bộ test chạy tay (TC-09, TC-10, TC-11, TC-12), thấy hai test FAIL và tự quyết định mức độ của BUG-005 và BUG-006.
- Ở BT3: chạy bảy lệnh kiểm bảo mật và tự quyết định trạng thái từng mục trong checklist.
- Ở BT3: tự chụp toàn bộ ảnh trong `docs/screenshots/`.
- Ở BT3: tự tạo tài khoản và dịch vụ trên Render, tự nhập biến môi trường, đổi mật khẩu MongoDB Atlas và chụp ảnh minh chứng deploy.
- Ở BT3: tự gõ mọi lệnh PowerShell, Git, Docker; commit riêng từng lỗi.
- Ở BT3: đọc, đối chiếu và viết lại các tài liệu trong `docs/` bằng lời của mình.

## 4. Xác nhận

Sinh viên xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Lê Thị Thùy Ngân, 2374802010328, ngày 12/11/2026