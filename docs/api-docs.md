# Tài liệu API - Hệ thống phiếu bảo hành Mekong Mobile (luồng L2)

Tài liệu này em viết cho 17 endpoint mà hệ thống đang có, không thêm endpoint nào chưa làm. Các ví dụ phản hồi em chép từ lần chạy thật ngày 11/11/2026 trên hệ thống chạy bằng Docker (em chạy bằng script `tools/api_samples.py`). Danh sách dài em rút gọn bớt, còn token em thay bằng `<token>`. Muốn thử trực tiếp thì mở `http://localhost:8000/docs`.

## 0. Những điều chung cho mọi endpoint

- Địa chỉ gốc: `http://localhost:8000`. Dữ liệu gửi và nhận là JSON (UTF-8). Request có thân thì gửi kèm `Content-Type: application/json`.
- Đăng nhập xong sẽ nhận một token (endpoint số 2). Các endpoint khác gửi token qua header `Authorization: Bearer <token>`. Token dùng được 8 giờ (`expires_in: 28800`).
- Thời gian viết theo chuẩn ISO 8601 có múi giờ, ví dụ `2026-11-11T17:08:09+07:00`.
- Khi có lỗi, hệ thống luôn trả cùng một dạng:

```json
{ "error": { "code": "NOT_FOUND", "message": "Không tìm thấy phiếu", "fields": {} } }
```

`fields` chỉ có nội dung khi lỗi nằm ở dữ liệu em gửi lên (cho biết trường nào sai và vì sao). Mỗi phản hồi lỗi còn có header `x-request-id` để tra trong nhật ký.

### Ai được làm gì

Bảng này em lấy từ `PERMISSIONS` trong `src/services/auth_service.py`. Sai vai trò thì bị 403; thiếu hoặc sai token thì bị 401.

| Việc | NHAN_VIEN (nhân viên) | QUAN_LY (quản lý) |
|---|---|---|
| Xem phiếu, loại lỗi, khách hàng, kỹ thuật viên, tổng quan | được | được |
| Tạo phiếu, phân loại, gán kỹ thuật viên, đổi trạng thái | được | không (403) |
| Ẩn (xóa mềm) phiếu | không (403) | được |
| Thêm, sửa, ngừng kỹ thuật viên; xem cả người đã ngừng | không (403) | được |

### Các mã lỗi

| Mã lỗi | HTTP | Khi nào gặp |
|---|---|---|
| `REQUIRED_FIELD_MISSING` | 400 | Thiếu một trường bắt buộc |
| `INVALID_FORMAT` | 400 | Dữ liệu sai định dạng hoặc sai giá trị (kể cả JSON hỏng, id không phải số) |
| `UNAUTHORIZED` | 401 | Chưa đăng nhập, token sai hoặc đã hết hạn |
| `INVALID_CREDENTIALS` | 401 | Sai tên đăng nhập hoặc mật khẩu |
| `FORBIDDEN` | 403 | Đã đăng nhập nhưng vai trò không được phép |
| `NOT_FOUND` | 404 | Không có phiếu, khách hàng, kỹ thuật viên hoặc loại lỗi đó |
| `INVALID_TRANSITION` | 409 | Chuyển trạng thái sai thứ tự |
| `TICKET_CLOSED` | 409 | Phiếu đã hoàn tất nên không gán được kỹ thuật viên |
| `DUPLICATE_CODE` | 409 | Mã kỹ thuật viên đã có người dùng |
| `INTERNAL_ERROR` | 500 | Lỗi ngoài dự kiến; phản hồi chỉ có mã tra cứu, không lộ chi tiết |
| `DB_UNAVAILABLE` | 503 | Không kết nối được MongoDB |

Ở từng endpoint em chỉ ghi những mã lỗi riêng của nó. Lỗi 401 (thiếu token), 500 và 503 thì endpoint nào cần đăng nhập cũng có thể gặp.

---

## Nhóm 1. Hệ thống và đăng nhập

### 1. GET /health

1. **Phương thức, đường dẫn:** `GET /health`
2. **Làm gì:** Kiểm tra ứng dụng còn chạy không và có nói chuyện được với MongoDB không. Docker dùng endpoint này cho healthcheck.
3. **Xác thực:** Không cần token.
4. **Tham số:** Không có.
5. **Phản hồi thành công:** 200

```json
{ "status": "ok", "db": "ok" }
```

6. **Mã lỗi:** Không có mã lỗi riêng.
7. **Lưu ý:** Khi không ping được MongoDB, endpoint này vẫn trả **200** nhưng `db` là `unreachable` (`{"status":"ok","db":"unreachable"}`). Nghĩa là healthcheck của Docker chỉ cho biết ứng dụng còn sống, chưa chắc cơ sở dữ liệu còn kết nối. Muốn chắc thì phải đọc trường `db`. Em để lại như vậy và ghi rõ ở đây.

### 2. POST /api/auth/login

1. **Phương thức, đường dẫn:** `POST /api/auth/login`
2. **Làm gì:** Đăng nhập bằng tên đăng nhập và mật khẩu, nhận token để gọi các endpoint khác.
3. **Xác thực:** Không cần token.
4. **Thân yêu cầu:**

| Trường | Kiểu | Bắt buộc | Ràng buộc |
|---|---|---|---|
| `username` | chuỗi | có | không được để trống |
| `password` | chuỗi | có | không được để trống |

```json
{ "username": "nhanvien01", "password": "<mat-khau>" }
```

5. **Phản hồi thành công:** 200

```json
{
  "access_token": "<token>",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": { "username": "nhanvien01", "full_name": "Võ Thanh Hương", "role": "NHAN_VIEN" }
}
```

6. **Mã lỗi:**

| HTTP | Mã | Ví dụ em đã chạy thật |
|---|---|---|
| 400 | `REQUIRED_FIELD_MISSING` | Thiếu `password`: `fields: {"password": "Vui lòng nhập mật khẩu"}` |
| 400 | `INVALID_FORMAT` | JSON bị hỏng |
| 401 | `INVALID_CREDENTIALS` | `"Sai tên đăng nhập hoặc mật khẩu"` |
| 503 | `DB_UNAVAILABLE` | MongoDB đang tắt |

7. **Lưu ý:** Hệ thống ép `username` về chuỗi trước khi tra cứu, nên nếu gửi một đối tượng như `{"$ne": null}` thì chỉ nhận 401 chứ không đăng nhập được. Mật khẩu trong cơ sở dữ liệu được băm bằng PBKDF2-SHA256.

### 3. GET /api/auth/me

1. **Phương thức, đường dẫn:** `GET /api/auth/me`
2. **Làm gì:** Cho biết ai đang đăng nhập, dựa vào token.
3. **Xác thực:** Cần token; vai trò nào cũng gọi được.
4. **Tham số:** Không có.
5. **Phản hồi thành công:** 200

```json
{ "username": "nhanvien01", "full_name": "Võ Thanh Hương", "role": "NHAN_VIEN" }
```

6. **Mã lỗi:** 401 `UNAUTHORIZED` (em chạy thật khi không gửi token: `"Vui lòng đăng nhập"`).
7. **Lưu ý:** Hệ thống chỉ nhận token do chính nó ký bằng `JWT_SECRET`. Token ký bằng khóa khác bị từ chối (đây là điều em đã sửa ở BUG-005).

---

## Nhóm 2. Phiếu bảo hành

### 4. POST /api/tickets

1. **Phương thức, đường dẫn:** `POST /api/tickets`
2. **Làm gì:** Tạo một phiếu bảo hành mới. Hệ thống tạo hồ sơ khách (hoặc gắn vào khách đã có theo số điện thoại) và tính hạn cam kết theo mức ưu tiên.
3. **Xác thực:** Cần token; quyền `ticket:create`, chỉ NHAN_VIEN.
4. **Thân yêu cầu:**

| Trường | Kiểu | Bắt buộc | Ràng buộc |
|---|---|---|---|
| `customer_name` | chuỗi | có | từ 1 đến 120 ký tự |
| `customer_phone` | chuỗi | có | được chuẩn hóa về 10 số bắt đầu bằng 0 (nhận `+84`, `84`, có dấu cách hoặc dấu chấm) |
| `issue_desc` | chuỗi | có | từ 10 đến 2000 ký tự |
| `priority` | chuỗi | không | `CAO`, `TRUNG_BINH` hoặc `THAP`; mặc định `TRUNG_BINH` |

```json
{ "customer_name": "Khách Thử API", "customer_phone": "0987 654 321",
  "issue_desc": "Màn hình bị sọc ngang sau khi rơi", "priority": "CAO" }
```

5. **Phản hồi thành công:** 201

```json
{
  "ticket_id": 61, "ticket_code": "BH-000605/2026", "customer_id": 61,
  "priority": "CAO", "status": "MOI", "technician_id": null,
  "received_at": "2026-11-11T17:08:09+07:00", "due_date": "2026-11-12T17:08:09+07:00"
}
```

6. **Mã lỗi:**

| HTTP | Mã | Ví dụ em đã chạy thật |
|---|---|---|
| 400 | `REQUIRED_FIELD_MISSING` | Thiếu số điện thoại: `fields: {"customer_phone": "Trường bắt buộc, không được để trống"}` |
| 400 | `INVALID_FORMAT` | Số điện thoại hoặc mô tả sai định dạng, `priority` không thuộc ba giá trị |
| 401 | `UNAUTHORIZED` | Chưa gửi token |
| 403 | `FORBIDDEN` | Tài khoản quản lý gửi yêu cầu này |

7. **Lưu ý:** Hạn cam kết (`due_date`) bằng lúc tiếp nhận cộng 24 giờ (CAO), 72 giờ (TRUNG_BINH) hoặc 120 giờ (THAP), và không tính Chủ nhật. Phiếu mới luôn ở trạng thái `MOI`, chưa có kỹ thuật viên và chưa có loại lỗi.

### 5. GET /api/tickets

1. **Phương thức, đường dẫn:** `GET /api/tickets`
2. **Làm gì:** Liệt kê phiếu (không gồm phiếu đã ẩn), có phân trang và có thể lọc.
3. **Xác thực:** Cần token; quyền `ticket:view`, vai trò nào cũng gọi được.
4. **Tham số truy vấn:**

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `status` | chuỗi | không | tất cả | `MOI`, `DANG_XU_LY` hoặc `HOAN_TAT` |
| `overdue` | boolean | không | `false` | `true` thì chỉ lấy phiếu chưa hoàn tất mà đã quá hạn |
| `page` | số nguyên | không | 1 | từ 1 trở lên |
| `size` | số nguyên | không | 20 | từ 1 đến 100 |

5. **Phản hồi thành công:** 200. Ví dụ `GET /api/tickets?size=2` (em rút gọn còn một phiếu):

```json
{
  "items": [
    {
      "ticket_id": 57, "ticket_code": "BH-000456/2026",
      "customer_name": "Lê Văn Hiếu", "customer_phone": "0969580438",
      "priority": "CAO", "status": "HOAN_TAT", "technician_name": "Phan Kim Nhung",
      "due_date": "2026-09-01T10:45:00+07:00", "due_state": null
    }
  ],
  "total": 60, "page": 1, "size": 2
}
```

`due_state` có ba giá trị: `QUA_HAN` (đã quá hạn), `SAP_DEN_HAN` (còn không quá 12 giờ) hoặc `null`. Khi em chạy thật, `?overdue=true&size=1` trả `total: 36` và phiếu có `"due_state": "QUA_HAN"`; `?status=HOAN_TAT&size=1` trả `total: 24`.

6. **Mã lỗi:** 400 `INVALID_FORMAT` (em chạy thật với `?status=XYZ`: `fields: {"status": "Trạng thái không hợp lệ"}`; `page` hoặc `size` ngoài khoảng cũng bị lỗi này), 401 `UNAUTHORIZED`.
7. **Lưu ý:** Mỗi trang tối đa 100 phiếu. Nếu vừa lọc `overdue=true` vừa lọc `status=HOAN_TAT` thì luôn ra danh sách rỗng, vì phiếu đã hoàn tất không bao giờ bị tính là quá hạn.

### 6. GET /api/tickets/{ticket_id}

1. **Phương thức, đường dẫn:** `GET /api/tickets/{ticket_id}`
2. **Làm gì:** Xem chi tiết một phiếu: hạn cam kết, cảnh báo, lịch sử trạng thái và lịch sử đổi kỹ thuật viên.
3. **Xác thực:** Cần token; quyền `ticket:view`, vai trò nào cũng gọi được.
4. **Tham số đường dẫn:** `ticket_id` (số nguyên dương).
5. **Phản hồi thành công:** 200. Ví dụ `GET /api/tickets/57` (em rút gọn phần lịch sử):

```json
{
  "ticket_id": 57, "ticket_code": "BH-000456/2026",
  "customer": { "customer_id": 13, "full_name": "Lê Văn Hiếu", "phone": "0969580438" },
  "technician": { "technician_id": 27, "technician_code": "KT027", "full_name": "Phan Kim Nhung" },
  "category": { "category_id": 1, "category_code": "MAN_HINH", "category_name": "Màn hình" },
  "issue_desc": "kh nói màn hình bị hở sáng viền dưới mới bị 2 ngày nay",
  "priority": "CAO", "status": "HOAN_TAT",
  "received_at": "2026-08-31T10:45:00+07:00", "due_date": "2026-09-01T10:45:00+07:00",
  "due_state": null, "remaining_minutes": null,
  "status_history": [
    { "from_status": null, "to_status": "MOI", "changed_at": "2026-08-31T10:45:00+07:00" },
    { "from_status": "MOI", "to_status": "DANG_XU_LY", "changed_at": "2026-08-31T12:35:00+07:00" }
  ],
  "assignment_history": [
    { "from_technician": null,
      "to_technician": { "technician_id": 27, "technician_code": "KT027", "full_name": "Phan Kim Nhung" },
      "changed_at": "2026-08-31T12:35:00+07:00" }
  ]
}
```

6. **Mã lỗi:** 400 `INVALID_FORMAT` (id không phải số), 401, 404 `NOT_FOUND` (em chạy thật với `/api/tickets/999999`: `"Không tìm thấy phiếu"`).
7. **Lưu ý:** Phiếu đã bị ẩn cũng trả 404, giống như phiếu không tồn tại. Id quá lớn (lớn hơn 9223372036854775807) cũng trả 404; trước đây trường hợp này làm hệ thống báo lỗi 500, em đã sửa ở BUG-006.

### 7. PATCH /api/tickets/{ticket_id}/category

1. **Phương thức, đường dẫn:** `PATCH /api/tickets/{ticket_id}/category`
2. **Làm gì:** Phân loại phiếu theo một loại lỗi.
3. **Xác thực:** Cần token; quyền `ticket:classify`, chỉ NHAN_VIEN.
4. **Thân yêu cầu:** `category_id` (số nguyên dương, bắt buộc, phải là một loại lỗi đang dùng).

```json
{ "category_id": 1 }
```

5. **Phản hồi thành công:** 200

```json
{ "ticket_id": 61, "category_id": 1, "category_code": "MAN_HINH" }
```

6. **Mã lỗi:** 400 (thiếu hoặc sai `category_id`), 401, 403 `FORBIDDEN` (quản lý gọi), 404 `NOT_FOUND` (em chạy thật với loại lỗi 99999: `"Không tìm thấy loại lỗi"`; hoặc không có phiếu đó).
7. **Lưu ý:** Một phiếu có thể phân loại lại nhiều lần. Hệ thống không lưu lịch sử đổi loại lỗi.

### 8. PATCH /api/tickets/{ticket_id}/technician

1. **Phương thức, đường dẫn:** `PATCH /api/tickets/{ticket_id}/technician`
2. **Làm gì:** Gán hoặc đổi kỹ thuật viên phụ trách phiếu.
3. **Xác thực:** Cần token; quyền `ticket:assign`, chỉ NHAN_VIEN.
4. **Thân yêu cầu:** `technician_id` (số nguyên dương, bắt buộc; kỹ thuật viên phải đang hoạt động).

```json
{ "technician_id": 2 }
```

5. **Phản hồi thành công:** 200

```json
{ "ticket_id": 61, "status": "MOI", "technician_id": 2, "changed_at": "2026-11-11T17:08:11+07:00" }
```

6. **Mã lỗi:** 400, 401, 403 `FORBIDDEN`, 404 `NOT_FOUND` (`"Không tìm thấy phiếu hoặc kỹ thuật viên"`), 409 `TICKET_CLOSED` (em chạy thật: `"Phiếu đã hoàn tất, không thể gán hoặc đổi kỹ thuật viên"`).
7. **Lưu ý:** Trạng thái phiếu không đổi khi gán. Mỗi lần đổi người đều được ghi vào lịch sử gán; nếu chọn lại đúng người cũ thì không ghi thêm. Kỹ thuật viên đã ngừng hoạt động thì không gán được.

### 9. PATCH /api/tickets/{ticket_id}/status

1. **Phương thức, đường dẫn:** `PATCH /api/tickets/{ticket_id}/status`
2. **Làm gì:** Chuyển phiếu sang trạng thái kế tiếp.
3. **Xác thực:** Cần token; quyền `ticket:status`, chỉ NHAN_VIEN.
4. **Thân yêu cầu:** `status` (bắt buộc): `MOI`, `DANG_XU_LY` hoặc `HOAN_TAT`.

```json
{ "status": "DANG_XU_LY" }
```

5. **Phản hồi thành công:** 200

```json
{ "ticket_id": 61, "status": "DANG_XU_LY", "changed_at": "2026-11-11T17:08:11+07:00" }
```

6. **Mã lỗi:** 400 (thiếu hoặc sai `status`), 401, 403, 404 `NOT_FOUND`, 409 `INVALID_TRANSITION` (em chạy thật khi gửi `MOI` cho phiếu đang xử lý: `"Sai thứ tự chuyển trạng thái"`).
7. **Lưu ý:** Chỉ đi một chiều `MOI` → `DANG_XU_LY` → `HOAN_TAT`: không nhảy cóc, không quay lại. Mỗi lần chuyển đều được ghi vào lịch sử trạng thái.

### 10. DELETE /api/tickets/{ticket_id}

1. **Phương thức, đường dẫn:** `DELETE /api/tickets/{ticket_id}`
2. **Làm gì:** Ẩn phiếu (xóa mềm). Dữ liệu vẫn được giữ lại nhưng phiếu không còn hiện ra.
3. **Xác thực:** Cần token; quyền `ticket:delete`, chỉ QUAN_LY.
4. **Tham số đường dẫn:** `ticket_id`.
5. **Phản hồi thành công:** 200

```json
{ "ticket_id": 61, "deleted_at": "2026-11-11T17:08:12+07:00" }
```

6. **Mã lỗi:** 401, 403 `FORBIDDEN` (em chạy thật khi nhân viên gọi), 404 `NOT_FOUND`.
7. **Lưu ý:** Không xóa cứng. Sau khi ẩn, `GET /api/tickets/{id}` trả 404 (em đã kiểm bằng lần chạy thật). Hệ thống chưa có endpoint khôi phục phiếu.

### 11. GET /api/overview

1. **Phương thức, đường dẫn:** `GET /api/overview`
2. **Làm gì:** Cho màn Tổng quan: số phiếu theo trạng thái, số phiếu quá hạn, số phiếu sắp đến hạn và năm phiếu cần chú ý nhất.
3. **Xác thực:** Cần token; quyền `overview:view`, vai trò nào cũng gọi được.
4. **Tham số:** Không có.
5. **Phản hồi thành công:** 200. Ví dụ em chạy thật (em rút gọn `attention` còn một phiếu; lúc đó trong hệ thống đã có thêm một phiếu em tạo thử nên `total` là 61):

```json
{
  "total": 61,
  "by_status": { "MOI": 0, "DANG_XU_LY": 36, "HOAN_TAT": 25 },
  "overdue": 36,
  "near_due": 0,
  "attention": [
    { "ticket_id": 44, "ticket_code": "BH-000166/2024", "customer_name": "Vũ Thị Phúc",
      "customer_phone": "0786491677", "priority": "CAO", "status": "DANG_XU_LY",
      "technician_name": "Phạm Văn Hạnh", "due_date": "2024-09-23T08:00:00+07:00",
      "due_state": "QUA_HAN" }
  ]
}
```

6. **Mã lỗi:** 401, 503.
7. **Lưu ý:** `attention` có tối đa 5 phiếu, ưu tiên phiếu hết hạn sớm nhất. Phiếu đã ẩn không được tính.

---

## Nhóm 3. Loại lỗi, khách hàng, kỹ thuật viên

### 12. GET /api/issue-categories

1. **Phương thức, đường dẫn:** `GET /api/issue-categories`
2. **Làm gì:** Lấy danh sách loại lỗi để chọn khi phân loại phiếu.
3. **Xác thực:** Cần token; quyền `ticket:view`, vai trò nào cũng gọi được.
4. **Tham số:** Không có.
5. **Phản hồi thành công:** 200 (có 6 loại, em rút gọn còn hai)

```json
{ "items": [
  { "category_id": 1, "category_code": "MAN_HINH", "category_name": "Màn hình" },
  { "category_id": 2, "category_code": "PIN", "category_name": "Pin" }
] }
```

Sáu mã: `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO`, `KHAC`.

6. **Mã lỗi:** 401.
7. **Lưu ý:** Danh sách này lấy từ dữ liệu mẫu và cố định. Hệ thống không có endpoint thêm hay sửa loại lỗi.

### 13. GET /api/customers

1. **Phương thức, đường dẫn:** `GET /api/customers?phone={phone}`
2. **Làm gì:** Tra cứu khách hàng theo số điện thoại, kèm tối đa 10 phiếu gần nhất của khách đó.
3. **Xác thực:** Cần token; quyền `customer:view`, vai trò nào cũng gọi được.
4. **Tham số truy vấn:** `phone` (bắt buộc). Số được chuẩn hóa giống lúc tạo phiếu (nhận `+84`, `84`, có dấu cách hoặc dấu chấm), sau đó phải đủ 10 số và bắt đầu bằng 0.
5. **Phản hồi thành công:** 200. Ví dụ em chạy thật `GET /api/customers?phone=0969580438`:

```json
{
  "customer_id": 13, "full_name": "Lê Văn Hiếu", "phone": "0969580438",
  "tickets": [
    { "ticket_id": 57, "ticket_code": "BH-000456/2026", "status": "HOAN_TAT",
      "received_at": "2026-08-31T10:45:00+07:00" }
  ]
}
```

6. **Mã lỗi:** 400 `REQUIRED_FIELD_MISSING` (thiếu `phone`), 400 `INVALID_FORMAT` (số sai định dạng), 401, 404 `NOT_FOUND` (em chạy thật với số `0000000000`: `"Không tìm thấy khách hàng"`).
7. **Lưu ý:** Chỉ tìm chính xác theo số điện thoại, không tìm theo tên. Mỗi số điện thoại chỉ có một hồ sơ khách.

### 14. GET /api/technicians

1. **Phương thức, đường dẫn:** `GET /api/technicians`
2. **Làm gì:** Lấy danh sách kỹ thuật viên để chọn khi gán phiếu.
3. **Xác thực:** Cần token; quyền `technician:view`, vai trò nào cũng gọi được.
4. **Tham số truy vấn:** `include_inactive` (boolean, mặc định `false`). Chỉ QUAN_LY dùng được; với NHAN_VIEN tham số này bị bỏ qua nên chỉ thấy người đang hoạt động.
5. **Phản hồi thành công:** 200 (em rút gọn). Ví dụ em chạy thật:

```json
{ "items": [
  { "technician_id": 2, "technician_code": "KT002", "full_name": "Trần Hoài Giang", "is_active": true },
  { "technician_id": 3, "technician_code": "KT003", "full_name": "Đặng Quang Oanh", "is_active": true }
] }
```

Khi quản lý gọi `?include_inactive=true` thì thấy thêm những người có `"is_active": false` (ví dụ `KT001`, `KT011`).

6. **Mã lỗi:** 401.
7. **Lưu ý:** Dữ liệu mẫu có 38 kỹ thuật viên, trong đó 2 người đã ngừng hoạt động. Danh sách không phân trang.

### 15. POST /api/technicians

1. **Phương thức, đường dẫn:** `POST /api/technicians`
2. **Làm gì:** Thêm một kỹ thuật viên mới.
3. **Xác thực:** Cần token; quyền `technician:manage`, chỉ QUAN_LY.
4. **Thân yêu cầu:**

| Trường | Kiểu | Bắt buộc | Ràng buộc |
|---|---|---|---|
| `technician_code` | chuỗi | có | chữ, số, gạch ngang hoặc gạch dưới, tối đa 20 ký tự; hệ thống đổi thành chữ in hoa |
| `full_name` | chuỗi | có | tối đa 120 ký tự |

```json
{ "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử" }
```

5. **Phản hồi thành công:** 201

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử", "is_active": true }
```

6. **Mã lỗi:** 400 (thiếu hoặc sai trường), 401, 403 `FORBIDDEN` (em chạy thật khi nhân viên gọi), 409 `DUPLICATE_CODE` (em chạy thật: `fields: {"technician_code": "Mã này đã được dùng"}`).
7. **Lưu ý:** Mã kỹ thuật viên không được trùng; gửi mã đã có thì nhận 409.

### 16. PATCH /api/technicians/{technician_id}

1. **Phương thức, đường dẫn:** `PATCH /api/technicians/{technician_id}`
2. **Làm gì:** Sửa tên hoặc bật/tắt trạng thái hoạt động của kỹ thuật viên.
3. **Xác thực:** Cần token; quyền `technician:manage`, chỉ QUAN_LY.
4. **Thân yêu cầu:** cần ít nhất một trong hai trường.

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| `full_name` | chuỗi | tối đa 120 ký tự |
| `is_active` | boolean | phải là `true` hoặc `false` |

```json
{ "full_name": "Kỹ thuật viên thử (đã sửa)" }
```

5. **Phản hồi thành công:** 200

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử (đã sửa)", "is_active": true }
```

6. **Mã lỗi:** 400 `REQUIRED_FIELD_MISSING` (em chạy thật khi gửi `{}`: `fields: {"body": "Cần ít nhất một trường: full_name hoặc is_active"}`), 400 `INVALID_FORMAT`, 401, 403, 404 `NOT_FOUND`.
7. **Lưu ý:** Sau khi tạo không đổi được `technician_code`.

### 17. DELETE /api/technicians/{technician_id}

1. **Phương thức, đường dẫn:** `DELETE /api/technicians/{technician_id}`
2. **Làm gì:** Cho kỹ thuật viên ngừng hoạt động (xóa mềm).
3. **Xác thực:** Cần token; quyền `technician:manage`, chỉ QUAN_LY.
4. **Tham số đường dẫn:** `technician_id`.
5. **Phản hồi thành công:** 200

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử (đã sửa)", "is_active": false }
```

6. **Mã lỗi:** 401, 403, 404 `NOT_FOUND`.
7. **Lưu ý:** Không xóa cứng, nên các phiếu cũ vẫn giữ được tên kỹ thuật viên. Gọi lại nhiều lần vẫn cho cùng kết quả. Người đã ngừng thì không còn trong danh sách chọn và không gán vào phiếu được; muốn bật lại thì dùng endpoint 16 với `{"is_active": true}`.