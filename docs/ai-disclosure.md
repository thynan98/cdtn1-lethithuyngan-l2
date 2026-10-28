# Phụ lục: Khai báo sử dụng AI

## 1. Công cụ AI đã dùng

- Claude (Anthropic): ở BT1 hỗ trợ viết nháp, rà soát và đối chiếu tài liệu; ở BT2 hỗ trợ soạn nháp mã nguồn, kiểm thử, ghi log, Docker, nhật ký lỗi và hướng dẫn chạy.
- Google Gemini (phần trả lời AI khi tìm trên Google): giải thích các khái niệm trong file API.
- Google Stitch (BT1): tạo bản nháp giao diện (Tạo phiếu, Danh sách phiếu, Chi tiết phiếu) từ câu lệnh mô tả của sinh viên, và sửa lại theo các yêu cầu sinh viên đưa ra.
- Figma AI (BT2): dựa trên các màn Stitch ở BT1, tạo bản nháp giao diện sinh động hơn (thêm màu sắc, chỉnh lại menu) và bổ sung các màn còn thiếu như Đăng nhập. Sinh viên không dùng mã do Figma sinh ra.

## 2. Bảng khai báo

| Phần của bài | Công cụ | Sinh viên dùng AI để làm gì | Sinh viên đã tự làm / chỉnh sửa gì | Cách sinh viên kiểm tra lại |
|---|---|---|---|---|
| SRS | Claude | Gợi ý cấu trúc, rà soát câu chữ, phát hiện chỗ chưa nhất quán giữa các mục | Sinh viên chọn phạm vi, viết lại các câu theo ý mình, quyết định US/FR/độ ưu tiên | Đối chiếu từng mục với case study và với use case, API, ERD |
| Use case và đặc tả | Claude | Góp ý cách nối actor với use case, gợi ý khung đặc tả | Sinh viên tự vẽ sơ đồ trên draw.io và viết lại đặc tả | Đối chiếu tên use case với bảng truy vết trong SRS |
| Kiến trúc | Claude | Gợi ý khung 4 tầng và cách diễn đạt "Vì NFR-xx…, tôi chọn…, đánh đổi là…" | Sinh viên vẽ và chỉnh sơ đồ, chọn NFR và ngưỡng, đọc hiểu rồi viết lại 3 câu bằng lời của mình | Kiểm tra ngưỡng NFR khớp với SRS mục 4 |
| Mô hình dữ liệu / ERD | Claude | Soạn nháp `data-model.md`, tạo bản nháp ERD để vẽ tiếp | Sinh viên chỉnh ERD trên draw.io (ký hiệu, quan hệ, ghi chú), chọn MongoDB đã được giảng viên đồng ý | Đối chiếu tên bảng, trường, kiểu dữ liệu với API và SRS |
| Wireframe | Google Stitch, Claude | Stitch tạo các bản nháp giao diện cho 3 màn hình từ câu lệnh mô tả; Claude giúp soạn câu lệnh gửi Stitch và rà soát nội dung màn | Sinh viên chọn 3 màn phù hợp trong các bản Stitch tạo ra, yêu cầu Stitch sửa lại cho khớp SRS (tiêu đề màn, bộ lọc trạng thái, mức ưu tiên), ghép 3 màn vào một ảnh và tự viết bảng ghi chú wireframe | So từng ô nhập, nút, bộ lọc trên màn với FR trong SRS và các trường trong API |
| Rà soát nhất quán giữa các tài liệu | Claude | Đối chiếu SRS, use case, API, data-model, ERD, wireframe và liệt kê chỗ lệch nhau | Sinh viên quyết định chọn cách sửa nào và tự sửa lại file của mình | Mở lại từng file sau khi sửa để xem đã khớp chưa |
| Tìm hiểu kiến thức (API contract) | Google Gemini | Hỏi để hiểu các thành phần trong file API, như endpoint, request/response, mã trạng thái, bảng validation | Sinh viên tự đọc lại, chỉnh file API cho khớp SRS và data-model | Đối chiếu từng endpoint với User Story và FR trong bảng truy vết |
| API contract (chỉ trong repo) | Claude | Soạn nháp endpoint và ví dụ request/response | Sinh viên đọc, hỏi lại chỗ chưa hiểu và chỉnh cho khớp SRS, dữ liệu | Mỗi endpoint truy vết về US/FR trong SRS |
| Mã nguồn backend (BT2) | Claude | Soạn nháp phần lớn mã nguồn các tầng routes, validators, services, repositories, migration và seed theo thiết kế BT1 và yêu cầu của sinh viên | Sinh viên đọc từng phần, hỏi lại chỗ chưa hiểu, chạy trên máy mình, chỉnh theo thiết kế và ghi các thay đổi vào `thay-doi-thiet-ke.md` | Chạy `pytest` (57 test pass), chạy migrate và seed hai lần để kiểm tra không nhân đôi dữ liệu, thử bằng giao diện với hai tài khoản |
| Bộ kiểm thử (BT2) | Claude | Soạn nháp các test (luồng đúng, giá trị biên, dữ liệu sai) và test hồi quy cho BUG-003 | Sinh viên chạy, đọc kết quả, hiểu từng test kiểm điều gì; tự tạm xóa dòng `.env` trong `.gitignore` để thấy test FAILED rồi khôi phục để thấy PASSED; tự commit | Chạy `python -m pytest -q` và đối chiếu từng test với quy tắc trong SRS mục 2.4; xem kết quả FAILED rồi PASSED của test BUG-003 |
| Ghi log và mã tra cứu lỗi (BT2) | Claude | Soạn nháp `logging_config.py`, middleware gắn mã tra cứu và 4 test | Sinh viên chạy hệ thống, tạo lỗi thật (làm mất kết nối cơ sở dữ liệu), chụp màn hình lỗi và dòng log có cùng mã tra cứu | Đối chiếu mã trên màn hình với dòng log; kiểm tra log không chứa số điện thoại, tên khách hay mật khẩu |
| Giao diện năm màn (BT2) | Claude, Figma AI | Figma AI, dựa trên các màn Stitch của BT1, tạo bản nháp giao diện sinh động hơn (thêm màu, chỉnh menu) và các màn còn thiếu (như Đăng nhập); Claude soạn nháp mã HTML, CSS, JavaScript theo wireframe BT1 và thiết kế trên Figma | Sinh viên tự viết phần mô tả trên Figma, tự chọn và chỉnh các bản nháp; không dùng mã do Figma sinh ra; chạy giao diện và thử ba trạng thái (đang tải, rỗng, lỗi) | Đối chiếu giao diện với wireframe và SRS; thử thủ công bằng hai tài khoản nhân viên và quản lý |
| Dữ liệu mẫu (BT2) | Claude | Gợi ý cách quy đổi 5 trạng thái của dữ liệu gốc về 3 trạng thái và soạn nháp `seed.py`, `make_sample.py` | Sinh viên chọn cách quy đổi, ghi vào TD-09, chạy seed trên cơ sở dữ liệu thật | Chạy seed lần hai báo "thêm 0"; đối chiếu số phiếu trên màn Tổng quan với dữ liệu mẫu |
| Docker (BT2) | Claude | Soạn nháp `Dockerfile`, `docker-compose.yml`, `.dockerignore` | Sinh viên cài Docker Desktop, tự chạy `docker compose up --build` và kiểm tra hệ thống lên được | Mở http://localhost:8000, đăng nhập và xem dữ liệu mẫu hiển thị đủ |
| Cài đặt và gỡ lỗi (BT2) | Claude | Hướng dẫn cài Docker và WSL, cấu hình kết nối MongoDB Atlas, giải thích và tìm nguyên nhân các lỗi khi chạy | Sinh viên làm theo hướng dẫn, tự chạy lệnh, chụp lỗi gửi lại và ghi các lỗi đã gặp vào `bug-log.md` (BUG-001 đến BUG-004) | Chạy lại sau mỗi lần sửa; đối chiếu với tài liệu buổi 11 về bốn bước gỡ lỗi |
| Quản lý phiên bản (BT2) | Claude | Gợi ý cách chia commit theo chức năng, cách viết thông điệp commit và hướng dẫn các lệnh Git | Sinh viên tự chạy lệnh Git, tự commit và đẩy lên GitHub | Xem lịch sử commit trên GitHub; chạy `git status` trước mỗi commit để chắc không có `.env` |
| Sơ đồ kiến trúc thực tế (BT2) | Claude | Chỉ ra những chỗ sơ đồ BT1 khác với code (đăng nhập, bảng `user`, màn Tổng quan) | Sinh viên tự vẽ lại sơ đồ trên draw.io theo hệ thống đã làm | Đối chiếu từng khối trong sơ đồ với thư mục `src/` |
| Nhật ký lỗi, README, thay đổi thiết kế (BT2) | Claude | Soạn nháp nội dung và khung trình bày | Sinh viên viết lại bằng lời của mình, kiểm tra từng dòng với repo và lịch sử commit | Mở lại từng link commit; làm theo README trên thư mục sạch |

## 3. Những phần không dùng AI

Các phần sau là của sinh viên:

- Chọn phạm vi, đề ra User Story, độ ưu tiên MoSCoW và các quy tắc nghiệp vụ trong SRS.
- Sơ đồ use case: sinh viên tự vẽ trên draw.io, tự nối actor với use case và viết đặc tả.
- Sơ đồ kiến trúc và ERD: sinh viên vẽ và chỉnh trên draw.io (bố cục, ký hiệu quan hệ, ghi chú), và tự viết các câu giải thích lựa chọn kiến trúc.
- Chọn công nghệ (Python FastAPI, MongoDB đã được giảng viên đồng ý) và các đánh đổi.
- Chọn 3 màn wireframe và viết bảng ghi chú.
- Ở BT2: tự viết phần mô tả (câu lệnh) trên Figma để thêm màu, chỉnh menu và bổ sung các màn còn thiếu; mã giao diện không lấy từ Figma.
- Đọc lại, chỉnh sửa và đối chiếu các tài liệu với nhau cho khớp.
- Ở BT2: tự chạy, thử và kiểm tra hệ thống (pytest, migrate, seed, giao diện, Docker), tự tạo lỗi thật để chụp ba trạng thái, tự vẽ lại sơ đồ kiến trúc thực tế, tự quyết định các thay đổi thiết kế và ghi vào `thay-doi-thiet-ke.md`, tự commit và đẩy lên GitHub.

## 4. Xác nhận

Sinh viên xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Lê Thị Thùy Ngân, 2374802010328, ngày 29/10/2026