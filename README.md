# Hệ thống tiếp nhận và theo dõi phiếu bảo hành của trung tâm Mekong Mobile (luồng L2)

Sinh viên: Lê Thị Thùy Ngân - 2374802010328 - Track SE

Học phần: Chuyên đề Tốt nghiệp 1, HK1 2026-2027

Luồng nghiệp vụ: L2 – Yêu cầu bảo hành (service desk)

## 1. Mục tiêu

Tại trung tâm bảo hành Mekong Mobile, yêu cầu bảo hành đang được ghi trên phiếu giấy nên khó biết phiếu đang ở bước nào, ai đang xử lý và đã quá hạn cam kết với khách hay chưa. Hệ thống này giúp nhân viên tiếp nhận ghi nhận yêu cầu thành phiếu, phân loại theo loại lỗi, gán kỹ thuật viên và theo dõi trạng thái từ lúc tiếp nhận đến khi hoàn tất. Hệ thống tính hạn cam kết theo mức ưu tiên và cảnh báo phiếu sắp hoặc đã quá hạn, để nhân viên và quản lý trung tâm biết phiếu nào cần xử lý hoặc can thiệp.

## 2. Yêu cầu môi trường

- Python 3.11 trở lên
- MongoDB (chạy cục bộ)
- Trình duyệt web hiện đại (giao diện HTML/CSS/JavaScript)
- Biến môi trường: xem `.env.example`

## 3. Hướng dẫn chạy


## 4. Cấu trúc thư mục


## 5. Kiểm thử


## 6. Trạng thái hiện tại

- [x] Tài liệu phân tích và thiết kế BT1 (SRS, use case, kiến trúc, ERD, wireframe, API contract) trong `docs/`
- [ ] Khởi tạo project, smoke test chạy được
- [ ] Module tạo phiếu bảo hành (US1)
- [ ] Module gán kỹ thuật viên (US3)
- [ ] Module cập nhật trạng thái phiếu (US4)
- [ ] Phân loại phiếu, xem hạn cam kết, xem và lọc danh sách phiếu, tra cứu khách hàng (US2, US5, US6, US7)