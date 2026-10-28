# API Contract – Hệ thống quản lý phiếu bảo hành (Mekong Mobile, luồng L2)

## 1. Quy ước chung

- Định dạng trao đổi: JSON, mã hóa UTF-8. Header bắt buộc: `Content-Type: application/json`. Mọi endpoint, trừ `POST /api/auth/login` và `GET /health`, còn cần header `Authorization: Bearer <token>` (xem mục 5).
- Tên trường dùng `snake_case`, khớp tên trường trong `docs/data-model.md` (MongoDB). Các `*_id` là số nguyên tự tăng do hệ thống cấp, không dùng ObjectId. Ngoại lệ: trong request tạo phiếu, `customer_name` và `customer_phone` được lưu vào `customer.full_name` và `customer.phone`.
- Thời gian dùng chuẩn ISO 8601 kèm múi giờ, ví dụ `2026-10-05T14:30:00+07:00`.
- Phân trang cho danh sách: tham số `page` (bắt đầu từ 1) và `size` (mặc định 20, tối đa 100). Response kèm `total`.
- Trạng thái phiếu dùng ba mã: `MOI` (Mới tiếp nhận), `DANG_XU_LY` (Đang xử lý), `HOAN_TAT` (Hoàn tất). Chỉ chuyển một chiều `MOI` → `DANG_XU_LY` → `HOAN_TAT`.
- Loại lỗi dùng các mã: `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO`, `KHAC`.
  Danh mục này lấy theo bảng `issue_category` (Mục 8 của case study).
- Mọi lỗi trả về cùng một cấu trúc:

```json
{ "error": { "code": "...", "message": "...", "fields": { } } }
```

## 2. Quy tắc nghiệp vụ liên quan

- Hạn cam kết (`due_date`, QT-04) = thời điểm tiếp nhận (`received_at`) + 24 giờ nếu `priority` là `CAO`, 72 giờ nếu `TRUNG_BINH`, 120 giờ nếu `THAP`; không tính Chủ nhật.
- Số điện thoại (QT-01, QT-02) được chuẩn hóa về 10 chữ số bắt đầu bằng 0 trước khi lưu; chấp nhận các dạng `+84…`, `84…`, có dấu cách hoặc dấu chấm. Mỗi số điện thoại chỉ có một hồ sơ khách.
- Phiếu "quá hạn" khi chưa `HOAN_TAT` và thời điểm hiện tại lớn hơn `due_date`. Phiếu "sắp đến hạn" khi chưa `HOAN_TAT`, chưa quá hạn và còn ≤ 12 giờ đến `due_date`. Hai giá trị này do hệ thống tự tính khi trả dữ liệu, không lưu như một trạng thái.
- Phiếu đã `HOAN_TAT` thì không gán hoặc đổi kỹ thuật viên.
- Khách hàng được nhận diện bằng số điện thoại: nếu số điện thoại đã có thì phiếu gắn vào hồ sơ khách đó, nếu chưa có thì hệ thống tạo hồ sơ khách mới.
- Xóa phiếu là xóa mềm (QT-13): phiếu có `deleted_at` không còn xuất hiện trong danh sách hay chi tiết, nhưng dữ liệu vẫn được giữ.
- Ghi nhận thiết bị và kiểm tra bảo hành nằm ngoài phạm vi, xem mục 1.2 của SRS.

## 3. Danh sách endpoint

| Phương thức | Đường dẫn | Mục đích | User Story | FR |
|---|---|---|---|---|
| POST | `/api/tickets` | Tạo phiếu bảo hành mới | US1 | FR-01, FR-02 |
| GET | `/api/issue-categories` | Lấy 6 loại lỗi để chọn | US2 | FR-03 |
| PATCH | `/api/tickets/{id}/category` | Phân loại phiếu theo loại lỗi | US2 | FR-03 |
| GET | `/api/technicians` | Lấy danh sách kỹ thuật viên để chọn | US3 | FR-04 |
| PATCH | `/api/tickets/{id}/technician` | Gán hoặc đổi kỹ thuật viên | US3 | FR-04 |
| PATCH | `/api/tickets/{id}/status` | Chuyển trạng thái phiếu | US4 | FR-05 |
| GET | `/api/tickets/{id}` | Xem phiếu kèm hạn cam kết, cảnh báo, lịch sử trạng thái và lịch sử đổi kỹ thuật viên | US5 | FR-06 |
| GET | `/api/tickets?status=&overdue=&page=&size=` | Danh sách phiếu, có lọc theo trạng thái hoặc quá hạn | US6 | FR-08, FR-09 |
| GET | `/api/customers?phone={phone}` | Tra cứu khách hàng theo số điện thoại | US7 | FR-07 |
| POST | `/api/auth/login` | Đăng nhập | Mở rộng (TD-05) | – |
| GET | `/api/auth/me` | Thông tin người đang đăng nhập | Mở rộng (TD-05) | – |
| DELETE | `/api/tickets/{id}` | Xóa mềm phiếu (chỉ QUAN_LY) | Mở rộng (TD-06) | – |
| POST, PATCH, DELETE | `/api/technicians`, `/api/technicians/{id}` | Thêm, sửa, ngừng hoạt động kỹ thuật viên (chỉ QUAN_LY) | Mở rộng (TD-06) | – |
| GET | `/api/overview` | Tổng quan: số phiếu theo trạng thái, quá hạn, sắp đến hạn, phiếu cần chú ý | Mở rộng (TD-08) | – |

Chi tiết bên dưới chỉ viết cho endpoint của các story MUST (US1, US3, US4).

## 4. Chi tiết endpoint

### 4.1 POST /api/tickets – Tạo phiếu bảo hành mới (US1)

Request body:

```json
{
  "customer_name": "Lê Thị Thùy Ngân",
  "customer_phone": "0912 345 678",
  "issue_desc": "Máy sạc không vào, cắm sạc báo lỗi phụ kiện",
  "priority": "TRUNG_BINH"
}
```

Response **201 Created** (tạo thành công):

```json
{
  "ticket_id": 88231,
  "ticket_code": "BH-000231/2026",
  "customer_id": 1024,
  "priority": "TRUNG_BINH",
  "status": "MOI",
  "technician_id": null,
  "received_at": "2026-10-05T14:30:00+07:00",
  "due_date": "2026-10-08T14:30:00+07:00"
}
```

Response **400 Bad Request** – thiếu trường bắt buộc:

```json
{
  "error": {
    "code": "REQUIRED_FIELD_MISSING",
    "message": "Dữ liệu không hợp lệ",
    "fields": { "customer_phone": "Trường bắt buộc, không được để trống" }
  }
}
```

Response **400 Bad Request** – sai định dạng:

```json
{
  "error": {
    "code": "INVALID_FORMAT",
    "message": "Dữ liệu không hợp lệ",
    "fields": { "customer_phone": "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0 (sau khi chuẩn hóa)" }
  }
}
```

Bảng validation:

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi khi vi phạm |
|---|---|---|---|
| `customer_name` | Có | Chuỗi, 1–120 ký tự | Tên khách hàng không được để trống |
| `customer_phone` | Có | Chuỗi; chuẩn hóa trước khi kiểm (QT-02), sau đó đúng 10 chữ số, bắt đầu bằng 0 | Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0 |
| `issue_desc` | Có | Chuỗi, 10–2000 ký tự | Mô tả lỗi phải có từ 10 đến 2000 ký tự |
| `priority` | Không | Một trong `CAO`, `TRUNG_BINH`, `THAP`; mặc định `TRUNG_BINH` | Mức ưu tiên không hợp lệ |

Truy vết: US1 (GWT1, GWT2, GWT3), FR-01, FR-02.

### 4.2 PATCH /api/tickets/{id}/technician – Gán hoặc đổi kỹ thuật viên (US3)

Request body:

```json
{ "technician_id": 12 }
```

Response **200 OK** (gán hoặc đổi thành công; trạng thái phiếu giữ nguyên, việc đổi người được lưu vào `ticket_assignment_log`: đổi lúc nào, từ kỹ thuật viên nào sang kỹ thuật viên nào):

```json
{
  "ticket_id": 88231,
  "status": "MOI",
  "technician_id": 12,
  "changed_at": "2026-10-05T15:10:00+07:00"
}
```

Response **404 Not Found** – không tìm thấy phiếu hoặc kỹ thuật viên:

```json
{ "error": { "code": "NOT_FOUND", "message": "Không tìm thấy phiếu hoặc kỹ thuật viên", "fields": { } } }
```

Response **409 Conflict** – phiếu đã hoàn tất:

```json
{ "error": { "code": "TICKET_CLOSED", "message": "Phiếu đã hoàn tất, không thể gán hoặc đổi kỹ thuật viên", "fields": { } } }
```

Bảng validation:

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi khi vi phạm |
|---|---|---|---|
| `technician_id` | Có | Số nguyên dương, phải tồn tại trong danh sách kỹ thuật viên | Không tìm thấy kỹ thuật viên |

Truy vết: US3 (GWT4, GWT5, GWT6), FR-04.

### 4.3 PATCH /api/tickets/{id}/status – Chuyển trạng thái phiếu (US4)

Request body:

```json
{ "status": "DANG_XU_LY" }
```

Response **200 OK** (chuyển thành công, lưu vào `ticket_status_log`):

```json
{
  "ticket_id": 88231,
  "status": "DANG_XU_LY",
  "changed_at": "2026-10-05T15:30:00+07:00"
}
```

Response **400 Bad Request** – giá trị trạng thái không hợp lệ:

```json
{ "error": { "code": "INVALID_FORMAT", "message": "Dữ liệu không hợp lệ", "fields": { "status": "Trạng thái không hợp lệ" } } }
```

Response **404 Not Found** – không tìm thấy phiếu:

```json
{ "error": { "code": "NOT_FOUND", "message": "Không tìm thấy phiếu", "fields": { } } }
```

Response **409 Conflict** – sai thứ tự trạng thái (ví dụ chuyển thẳng `MOI` sang `HOAN_TAT`):

```json
{ "error": { "code": "INVALID_TRANSITION", "message": "Sai thứ tự chuyển trạng thái", "fields": { } } }
```

Bảng validation:

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi khi vi phạm |
|---|---|---|---|
| `status` | Có | Một trong `MOI`, `DANG_XU_LY`, `HOAN_TAT`; chỉ được chuyển sang trạng thái kế tiếp | Trạng thái không hợp lệ |

Truy vết: US4 (GWT7, GWT8), FR-05.

## 5. Xác thực và phân quyền

### 5.1 Xác thực

Từ BT2 hệ thống có đăng nhập (TD-05). Mọi endpoint, trừ `POST /api/auth/login` và `GET /health`, cần header `Authorization: Bearer <token>`. Thiếu hoặc sai token trả 401 `UNAUTHORIZED`.

| Endpoint | Mô tả | Thành công | Lỗi thường gặp |
|---|---|---|---|
| POST `/api/auth/login` | body `{username, password}` | 200 `{access_token, token_type, expires_in, user}` | 400 thiếu trường, 401 `INVALID_CREDENTIALS` |
| GET `/api/auth/me` | thông tin người đang đăng nhập | 200 | 401 `UNAUTHORIZED` |

### 5.2 Quyền theo vai trò

Đúng token nhưng vai trò không có quyền trả 403 `FORBIDDEN`.

| Việc | NHAN_VIEN | QUAN_LY |
|---|---|---|
| Xem phiếu, khách hàng, kỹ thuật viên, tổng quan | có | có |
| Tạo phiếu, phân loại, gán/đổi kỹ thuật viên, đổi trạng thái | có | không (403) |
| Xóa (ẩn) phiếu | không (403) | có |
| Thêm, sửa, ngừng kỹ thuật viên | không (403) | có |

### 5.3 Bảng mã lỗi

| Mã lỗi | HTTP | Khi nào xảy ra |
|---|---|---|
| `REQUIRED_FIELD_MISSING` | 400 | Thiếu trường bắt buộc |
| `INVALID_FORMAT` | 400 | Sai định dạng hoặc giá trị không hợp lệ |
| `UNAUTHORIZED` | 401 | Thiếu, sai hoặc hết hạn token |
| `INVALID_CREDENTIALS` | 401 | Sai tên đăng nhập hoặc mật khẩu |
| `FORBIDDEN` | 403 | Vai trò không có quyền thực hiện |
| `NOT_FOUND` | 404 | Không tìm thấy phiếu, kỹ thuật viên, khách hàng hoặc loại lỗi |
| `INVALID_TRANSITION` | 409 | Chuyển trạng thái sai thứ tự |
| `TICKET_CLOSED` | 409 | Phiếu đã hoàn tất, không gán hoặc đổi kỹ thuật viên |
| `DUPLICATE_CODE` | 409 | Mã kỹ thuật viên đã tồn tại |
| `DB_UNAVAILABLE` | 503 | Không truy cập được cơ sở dữ liệu |
| `INTERNAL_ERROR` | 500 | Lỗi không dự kiến; không lộ chi tiết kỹ thuật |

## 6. Tự kiểm trước khi nộp

- [x] Mỗi endpoint nối được về ít nhất một User Story trong bảng truy vết của SRS, trừ các endpoint mở rộng đã ghi TD-05, TD-06, TD-08 trong bảng mục 3.
- [x] Mỗi endpoint chi tiết có ≥ 1 response thành công và ≥ 2 response lỗi.
- [x] Mọi trường trong request và response đều có trong ERD (`docs/data-model.md`, đã bổ sung `user`, `deleted_at`, `is_active`).
- [x] Mã lỗi 401, 403, 503 đã có trong bảng mã lỗi (mục 5.3).
- [x] Quy tắc QT-01, QT-02, QT-04, QT-06, QT-13 đã xuất hiện trong mục 2, bảng validation hoặc mã lỗi.
