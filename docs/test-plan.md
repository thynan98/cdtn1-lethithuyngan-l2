# Test Plan - Luồng L2: Yêu cầu bảo hành

## 1. Phạm vi

**Nội dung được kiểm thử:**
- Tạo phiếu và kiểm tra dữ liệu vào (số điện thoại, mô tả lỗi).
- Quy tắc tính hạn cam kết (QT-04) và chuẩn hóa số điện thoại (QT-02).
- Quy tắc chuyển trạng thái một chiều (QT-06).
- Đăng nhập và phân quyền giữa nhân viên và quản lý.
- Chạy lại seed không làm nhân đôi dữ liệu.

**Nội dung không kiểm thử và lý do:**
- Hiệu năng khi nhiều người dùng cùng lúc: thuộc Chuyên đề tốt nghiệp 2.
- Giao diện bằng công cụ tự động: em chỉ thử tay trên trình duyệt.
- Thiết bị và kiểm tra bảo hành: ngoài phạm vi SRS (mục 1.2).
- Giới hạn số lần đăng nhập sai: hệ thống chưa có chức năng này.
- Gán kỹ thuật viên, tra cứu khách, xóa mềm (QT-01, QT-13): đã có test trong bộ 68
  test tự động, nhưng em không đưa vào 12 test case của báo cáo.

## 2. Loại test và số lượng

| Tầng | Số lượng | Test case | Cách chạy |
|---|---|---|---|
| Unit (hàm và validator, không cần MongoDB) | 8 | TC-01 đến TC-08 | `pytest` |
| API qua TestClient (dùng kho giả) | 1 | TC-10 | `pytest`, và chạy lại tay trên hệ thống thật |
| Chạy tay trên hệ thống thật (Docker + MongoDB) | 3 | TC-09, TC-11, TC-12 | curl, mongosh và `seeds.seed` |

Tổng cộng 12 test case, đủ 5 loại: luồng đúng (3), giá trị biên (3), dữ liệu sai (3),
bảo mật (2), tái lập (1).

Cách chọn dữ liệu thử: em chia mô tả lỗi thành ba vùng (dưới 10 ký tự, từ 10 đến 2000,
trên 2000) và thử đúng hai bên ranh giới 10 ký tự (9 và 10). Với hạn cam kết, em thử
thứ Bảy mức CAO để kiểm tra việc bỏ qua Chủ nhật.

Bộ 68 test tự động (`pytest`) là lưới an toàn: em chạy lại sau mỗi lần sửa bug để
chắc không làm hỏng chỗ khác.

## 3. Tiêu chí thành công

- 12/12 test case có kết quả thực tế ghi cụ thể và có ảnh chụp trong `docs/screenshots/`.
- Mỗi quy tắc nằm trong báo cáo (QT-02, QT-04, QT-06) có ít nhất một test luồng đúng
  và một test sai hoặc giá trị biên.
- Không còn bug mức Critical đang mở; bug Major còn lại có lý do và hướng xử lý.
- Sau khi sửa bug, `python -m pytest -q` chạy PASS toàn bộ chỉ bằng một lệnh.

## 4. Môi trường và dữ liệu thử

- Máy Windows, Python 3.14, Docker Desktop.
- Test tự động: `python -m pytest -q`. Test dùng kho dữ liệu giả nên không cần MongoDB
  và không phụ thuộc dữ liệu có sẵn trên máy.
- Test chạy tay: dựng hệ thống mới bằng `docker compose down -v` rồi
  `docker compose up --build`. Dữ liệu mẫu trong `data/sample` (38 kỹ thuật viên,
  6 loại lỗi, 60 phiếu) do `seeds.seed` nạp tự động. Dùng hai tài khoản `nhanvien01`
  và `quanly01`.