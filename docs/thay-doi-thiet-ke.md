## TD-01. Thêm cột "Không được làm" cho vai trò ở SRS mục 2.1
- Đã đổi: em thêm cột "Không được làm" cho hai vai trò, nhân viên tiếp nhận và quản lý trung tâm, ở SRS mục 2.1.
- Vì sao: giảng viên nhận xét BT1 chưa nói rõ mỗi vai trò bị cấm làm gì, nên chưa đủ căn cứ để phân quyền.
- Ảnh hưởng: chỉ SRS mục 2.1 (bản 1.1); cột này là căn cứ cho bảng quyền ở mục 5 của `docs/api-contract.md`.
- Nguồn: nhận xét BT1 của giảng viên.

## TD-02. Sửa tiêu đề mục 3.1 của SRS
- Đã đổi: em sửa tiêu đề SRS mục 3.1 thành "User Story và mức ưu tiên MoSCoW" (trước đó là "Quy tắc nghiệp vụ").
- Vì sao: giảng viên nhận xét tiêu đề mục này chưa đúng với nội dung của mục.
- Ảnh hưởng: chỉ SRS mục 3.1, không đổi API hay cơ sở dữ liệu.
- Nguồn: nhận xét BT1 của giảng viên.

## TD-03. Đưa mô hình dữ liệu vào repo
- Đã đổi: em thêm `docs/data-model.md` vào repo (ERD 3NF và khai báo các collection MongoDB).
- Vì sao: ở BT1 mô hình dữ liệu chưa nằm trong repo nên giảng viên yêu cầu bổ sung.
- Ảnh hưởng: `docs/data-model.md` là căn cứ để viết `migrations/migrate.py`; tên trường trong API khớp với file này.
- Nguồn: nhận xét BT1 của giảng viên.

## TD-04. Dựng cơ sở dữ liệu bằng migration thay cho db/schema.sql
- Đã đổi: em dựng cơ sở dữ liệu bằng `migrations/migrate.py` (JSON Schema và chỉ mục duy nhất) và bỏ file `db/schema.sql`.
- Vì sao: hệ thống dùng MongoDB (công nghệ đã duyệt, không đổi được) nên không có bảng SQL; giảng viên đã đồng ý "chốt ở Bài tập 1".
- Ảnh hưởng: cấu trúc cơ sở dữ liệu chỉ còn một nguồn là `migrations/migrate.py`, còn `docs/data-model.md` là bản mô tả; chạy migration trên DB trống là có đủ collection và chỉ mục.

## TD-05. Thêm đăng nhập và đăng xuất
- Đã đổi: em thêm màn Đăng nhập, nút Đăng xuất, và hai API `POST /api/auth/login`, `GET /api/auth/me`. Các API còn lại (trừ `GET /health`) giờ đều cần token.
- Vì sao: SRS mục 2.1 có hai vai trò (nhân viên tiếp nhận, quản lý) nên hệ thống phải biết ai đang dùng thì mới phân quyền được.
- Ảnh hưởng: thêm collection `user` (mật khẩu chỉ lưu bản băm), thêm mã lỗi 401 `UNAUTHORIZED`, `INVALID_CREDENTIALS` và 403 `FORBIDDEN`.

## TD-06. Đổi menu, thêm xóa mềm phiếu và quyền của Quản lý
- Đã đổi: em để menu chỉ còn "Tổng quan" và "Danh sách phiếu". Em thêm nút "Xóa phiếu" (có hộp xác nhận; thực chất chỉ ẩn phiếu, dữ liệu vẫn còn nên gọi là xóa mềm) và API quản lý kỹ thuật viên, phần kỹ thuật viên không làm màn riêng.
- Vì sao: QT-13 không cho xóa cứng, nhưng cần có người ẩn phiếu nhập nhầm và ngừng kỹ thuật viên đã nghỉ việc. SRS không nói vai trò nào làm việc này nên em giao cho Quản lý trung tâm.
- Ảnh hưởng: phiếu có thêm `deleted_at`, kỹ thuật viên có thêm `is_active`; thêm `DELETE /api/tickets/{id}` và nhóm `/api/technicians`. Đây là phần em mở rộng ngoài SRS, mong giảng viên xác nhận.

## TD-07. Bỏ các mục ngoài SRS và thêm 3 trạng thái giao diện
- Đã đổi: em bỏ những mục chỉ có trên wireframe mà SRS không yêu cầu. Mỗi màn có đủ ba trạng thái: đang tải, rỗng, lỗi (có nút Thử lại).
- Vì sao: để giữ đúng phạm vi luồng L2 và đáp ứng yêu cầu ba trạng thái của BT2.
- Ảnh hưởng: mọi trang gọi API qua một lớp client chung (`frontend/js/api/`) và dùng chung một thành phần hiển thị trạng thái.

## TD-08. Thêm màn Tổng quan
- Đã đổi: em thêm màn Tổng quan gồm số phiếu theo trạng thái, số phiếu quá hạn, sắp đến hạn và danh sách phiếu cần chú ý; thêm API `GET /api/overview`.
- Vì sao: để quản lý nhìn nhanh tình hình trong ngày, và màn này chỉ dùng lại dữ liệu có sẵn nên không cần thêm bảng mới.
- Ảnh hưởng: "sắp đến hạn" (còn không quá 12 giờ) và "quá hạn" được tính khi xem, không lưu vào cơ sở dữ liệu.

## TD-09. Dùng dữ liệu mẫu của case study thay cho dữ liệu tự tạo
- Đã đổi: ở bản đầu em tự tạo ít dữ liệu để chạy thử. Giờ em dùng dữ liệu mẫu của case study, bản nhỏ nằm trong `data/sample/` (38 kỹ thuật viên, 6 loại lỗi, 60 phiếu cùng khách hàng và nhật ký trạng thái). Dữ liệu gốc có 5 trạng thái, em gộp lại còn 3 trạng thái như thiết kế. Hạn cam kết em tính lại theo QT-04 chứ không lấy cột hạn trong file gốc.
- Vì sao: đề yêu cầu dùng dữ liệu của case study. Dữ liệu gốc tính hạn theo cách khác và có nhiều trạng thái hơn thiết kế của em, nên em phải quy đổi để khớp.
- Ảnh hưởng: `seeds/seed.py`, thư mục `data/sample/`, `tools/make_sample.py`. Mã kỹ thuật viên đổi sang dạng KT001. Thông tin trung tâm bảo hành và bậc tay nghề trong dữ liệu gốc em không dùng vì ngoài phạm vi.

## TD-10. Thêm ghi log và mã tra cứu khi có lỗi
- Đã đổi: em thêm ghi log dạng JSON ở máy chủ (`src/logging_config.py`) và gắn một mã tra cứu cho mỗi yêu cầu. Khi có lỗi hệ thống, màn hình hiện "Mã tra cứu: ..." và dòng log của lỗi đó có cùng mã.
- Vì sao: để khi có người báo lỗi thì em tìm đúng dòng log ngay, không phải đoán. Màn hình cũng không hiện chi tiết nội bộ hay thông tin của khách.
- Ảnh hưởng: `src/main.py`, `src/services/ticket_service.py`, thêm `tests/test_logging.py`. Log không ghi số điện thoại, tên khách hay mật khẩu. Em thêm biến `LOG_LEVEL` vào `.env.example`.

## TD-11. Đóng gói bằng Docker
- Đã đổi: em thêm `Dockerfile`, `docker-compose.yml` và `.dockerignore`. Chỉ cần chạy `docker compose up --build` là có cả hệ thống lẫn MongoDB, hệ thống tự tạo collection và nạp dữ liệu mẫu.
- Vì sao: để người khác dựng lại hệ thống bằng một lệnh, không phải tự cài MongoDB và Python.
- Ảnh hưởng: chỉ thêm ba file ở thư mục gốc, mã nguồn không đổi. Em vẫn chạy trực tiếp bằng Python được như hướng dẫn trong README.

## TD-12. Cập nhật SRS lên bản 1.2
- Đã đổi: ở SRS mục 1.2, 2.1, 2.2 và 2.4 em thêm ghi chú trỏ tới TD-05 (đăng nhập) và TD-06 (xóa mềm). Em giữ nguyên nội dung gốc của BT1.
- Vì sao: SRS ở BT1 ghi đăng nhập là ngoài phạm vi và ghi hệ thống không có chức năng xóa, nhưng em đã làm cả hai ở BT2. Em thêm ghi chú để SRS không nói ngược với hệ thống.
- Ảnh hưởng: chỉ `docs/srs.md`, không đổi mã nguồn.

## TD-13. Thêm CategoryService để route loại lỗi không gọi thẳng repository
- Đã đổi: em thêm `src/services/category_service.py`. Route `GET /api/issue-categories` giờ gọi service, service mới gọi repository.
- Vì sao: ở bản đầu route này đi thẳng vào repository, bỏ qua tầng service, không đúng thiết kế 4 tầng của BT1 (routes → services → repositories).
- Ảnh hưởng: `src/routes/categories.py`, `src/dependencies.py`, `tests/test_api.py`. Kết quả API không đổi, vẫn 57 test PASS. Đây là sửa cho đúng thiết kế, không đổi chức năng.

