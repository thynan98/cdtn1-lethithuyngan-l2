# Phụ lục: Khai báo sử dụng AI

## 1. Công cụ AI đã dùng

- Claude (Anthropic): hỗ trợ viết nháp, rà soát và đối chiếu tài liệu.
- Google Gemini (phần trả lời AI khi tìm trên Google): giải thích các khái niệm trong file API.
- Google Stitch: tạo bản nháp giao diện (Tạo phiếu, Danh sách phiếu, Chi tiết phiếu) từ câu lệnh mô tả của sinh viên, và sửa lại theo các yêu cầu sinh viên đưa ra.

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

## 3. Những phần không dùng AI

Các phần sau là của sinh viên:

- Chọn phạm vi, đề ra User Story, độ ưu tiên MoSCoW và các quy tắc nghiệp vụ trong SRS.
- Sơ đồ use case: sinh viên tự vẽ trên draw.io, tự nối actor với use case và viết đặc tả.
- Sơ đồ kiến trúc và ERD: sinh viên vẽ và chỉnh trên draw.io (bố cục, ký hiệu quan hệ, ghi chú), và tự viết các câu giải thích lựa chọn kiến trúc.
- Chọn công nghệ (Python FastAPI, MongoDB đã được giảng viên đồng ý) và các đánh đổi.
- Chọn 3 màn wireframe và viết bảng ghi chú.
- Đọc lại, chỉnh sửa và đối chiếu các tài liệu với nhau cho khớp.

## 4. Xác nhận

Sinh viên xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Lê Thị Thùy Ngân, 2374802010328, ngày 08/10/2026