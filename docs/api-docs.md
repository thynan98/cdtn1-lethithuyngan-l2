# API Documentation - Mekong Mobile Warranty Ticket System (flow L2)

This document describes the 17 endpoints the system really has. I did not describe any endpoint that does not exist. The example responses were copied from a real run on 11/11/2026 against the system running in Docker (I ran the script `tools/api_samples.py`). Long lists are shortened, and tokens are replaced by `<token>`. To try the API in the browser, open `http://localhost:8000/docs`.

## 0. Common rules

- Base URL: `http://localhost:8000`. Requests and responses are JSON (UTF-8). A request with a body must send `Content-Type: application/json`.
- Log in first (endpoint 2) to get a token. Every other endpoint, except `GET /health`, needs the header `Authorization: Bearer <token>`. A token is valid for 8 hours (`expires_in: 28800`).
- Times use ISO 8601 with a time zone, for example `2026-11-11T17:08:09+07:00`.
- Every error has the same shape:

```json
{ "error": { "code": "NOT_FOUND", "message": "Không tìm thấy phiếu", "fields": {} } }
```

`fields` has content only when the problem is in the data that was sent (it names the field and the reason). Error responses also carry the header `x-request-id`, which is used to find the matching log line. The `message` texts are in Vietnamese, because the interface is Vietnamese.

### Who can do what

This table comes from `PERMISSIONS` in `src/services/auth_service.py`. A wrong role gets 403. A missing or invalid token gets 401.

| Action | NHAN_VIEN (receptionist) | QUAN_LY (manager) |
|---|---|---|
| View tickets, issue categories, customers, technicians, overview | yes | yes |
| Create a ticket, set its category, assign a technician, change its status | yes | no (403) |
| Hide (soft-delete) a ticket | no (403) | yes |
| Add, edit, deactivate technicians; see deactivated technicians | no (403) | yes |

### Error codes

| Code | HTTP | When |
|---|---|---|
| `REQUIRED_FIELD_MISSING` | 400 | A required field is missing |
| `INVALID_FORMAT` | 400 | Wrong format or value (also broken JSON, or an id that is not a number) |
| `UNAUTHORIZED` | 401 | Not logged in, or the token is invalid or expired |
| `INVALID_CREDENTIALS` | 401 | Wrong username or password |
| `FORBIDDEN` | 403 | Logged in, but the role is not allowed |
| `NOT_FOUND` | 404 | The ticket, customer, technician or issue category does not exist |
| `INVALID_TRANSITION` | 409 | The status change is in the wrong order |
| `TICKET_CLOSED` | 409 | The ticket is completed, so a technician cannot be assigned |
| `DUPLICATE_CODE` | 409 | The technician code is already used |
| `INTERNAL_ERROR` | 500 | Unexpected error; the response has only a lookup code and no technical detail |
| `DB_UNAVAILABLE` | 503 | MongoDB cannot be reached |

For each endpoint below I list only the error codes that are specific to it. Every endpoint that needs a token can also return 401 (missing token), 500 and 503.

---

## Group 1. System and login

### 1. GET /health

1. **Method and path:** `GET /health`
2. **Description:** Checks that the application is running and that it can ping MongoDB. Docker uses this endpoint for the container healthcheck.
3. **Authentication:** No token needed.
4. **Parameters:** None.
5. **Success response:** 200

```json
{ "status": "ok", "db": "ok" }
```

6. **Error codes:** None of its own.
7. **Notes:** When MongoDB cannot be pinged, this endpoint still returns **200**, but `db` becomes `unreachable` (`{"status":"ok","db":"unreachable"}`). So the Docker healthcheck only proves that the application is alive, not that the database is connected. To be sure, read the `db` field. I left it this way and I write it down here.

### 2. POST /api/auth/login

1. **Method and path:** `POST /api/auth/login`
2. **Description:** Logs in with a username and password and returns a token for the other endpoints.
3. **Authentication:** No token needed.
4. **Request body:**

| Field | Type | Required | Rule |
|---|---|---|---|
| `username` | string | yes | must not be empty |
| `password` | string | yes | must not be empty |

```json
{ "username": "nhanvien01", "password": "<password>" }
```

5. **Success response:** 200

```json
{
  "access_token": "<token>",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": { "username": "nhanvien01", "full_name": "Võ Thanh Hương", "role": "NHAN_VIEN" }
}
```

6. **Error codes:**

| HTTP | Code | Real example from my run |
|---|---|---|
| 400 | `REQUIRED_FIELD_MISSING` | `password` missing: `fields: {"password": "Vui lòng nhập mật khẩu"}` |
| 400 | `INVALID_FORMAT` | broken JSON |
| 401 | `INVALID_CREDENTIALS` | `"Sai tên đăng nhập hoặc mật khẩu"` (wrong username or password) |
| 503 | `DB_UNAVAILABLE` | MongoDB is stopped |

7. **Notes:** The system turns `username` into a string before looking it up. If an object such as `{"$ne": null}` is sent, the result is only 401 and nobody is logged in. Passwords are stored as PBKDF2-SHA256 hashes.

### 3. GET /api/auth/me

1. **Method and path:** `GET /api/auth/me`
2. **Description:** Tells who is logged in, based on the token.
3. **Authentication:** Token required; any role.
4. **Parameters:** None.
5. **Success response:** 200

```json
{ "username": "nhanvien01", "full_name": "Võ Thanh Hương", "role": "NHAN_VIEN" }
```

6. **Error codes:** 401 `UNAUTHORIZED` (real example without a token: `"Vui lòng đăng nhập"`).
7. **Notes:** The system accepts only tokens that it signed itself with `JWT_SECRET`. A token signed with another key is rejected (this is what I fixed in BUG-005).

---

## Group 2. Warranty tickets

### 4. POST /api/tickets

1. **Method and path:** `POST /api/tickets`
2. **Description:** Creates a new warranty ticket. The system creates a customer record (or links to the existing customer with the same phone number) and calculates the due date from the priority.
3. **Authentication:** Token required; permission `ticket:create` (NHAN_VIEN only).
4. **Request body:**

| Field | Type | Required | Rule |
|---|---|---|---|
| `customer_name` | string | yes | 1 to 120 characters |
| `customer_phone` | string | yes | normalized to 10 digits starting with 0 (accepts `+84`, `84`, spaces and dots) |
| `issue_desc` | string | yes | 10 to 2000 characters |
| `priority` | string | no | `CAO`, `TRUNG_BINH` or `THAP`; default `TRUNG_BINH` |

```json
{ "customer_name": "Khách Thử API", "customer_phone": "0987 654 321",
  "issue_desc": "Màn hình bị sọc ngang sau khi rơi", "priority": "CAO" }
```

5. **Success response:** 201

```json
{
  "ticket_id": 61, "ticket_code": "BH-000605/2026", "customer_id": 61,
  "priority": "CAO", "status": "MOI", "technician_id": null,
  "received_at": "2026-11-11T17:08:09+07:00", "due_date": "2026-11-12T17:08:09+07:00"
}
```

6. **Error codes:**

| HTTP | Code | Real example from my run |
|---|---|---|
| 400 | `REQUIRED_FIELD_MISSING` | phone missing: `fields: {"customer_phone": "Trường bắt buộc, không được để trống"}` |
| 400 | `INVALID_FORMAT` | phone or description in the wrong format, or `priority` not one of the three values |
| 401 | `UNAUTHORIZED` | no token sent |
| 403 | `FORBIDDEN` | a manager account sent this request |

7. **Notes:** The due date (`due_date`) is the receive time plus 24 hours (CAO), 72 hours (TRUNG_BINH) or 120 hours (THAP), and Sundays are not counted. A new ticket always starts with status `MOI`, no technician and no category.

### 5. GET /api/tickets

1. **Method and path:** `GET /api/tickets`
2. **Description:** Lists tickets (hidden tickets are not included), with paging and filters.
3. **Authentication:** Token required; permission `ticket:view` (any role).
4. **Query parameters:**

| Parameter | Type | Required | Default | Rule |
|---|---|---|---|---|
| `status` | string | no | all | `MOI`, `DANG_XU_LY` or `HOAN_TAT` |
| `overdue` | boolean | no | `false` | `true` returns only tickets that are not completed and are past their due date |
| `page` | integer | no | 1 | 1 or more |
| `size` | integer | no | 20 | 1 to 100 |

5. **Success response:** 200. Example for `GET /api/tickets?size=2` (shortened to one ticket):

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

`due_state` has three values: `QUA_HAN` (overdue), `SAP_DEN_HAN` (due within 12 hours) or `null`. In my real run, `?overdue=true&size=1` returned `total: 36` with `"due_state": "QUA_HAN"`, and `?status=HOAN_TAT&size=1` returned `total: 24`.

6. **Error codes:** 400 `INVALID_FORMAT` (real example with `?status=XYZ`: `fields: {"status": "Trạng thái không hợp lệ"}`; a `page` or `size` outside its range gives the same error), 401 `UNAUTHORIZED`.
7. **Notes:** A page holds at most 100 tickets. If `overdue=true` is combined with `status=HOAN_TAT`, the list is always empty, because a completed ticket is never counted as overdue.

### 6. GET /api/tickets/{ticket_id}

1. **Method and path:** `GET /api/tickets/{ticket_id}`
2. **Description:** Shows one ticket in detail: due date, warning, status history and technician history.
3. **Authentication:** Token required; permission `ticket:view` (any role).
4. **Path parameter:** `ticket_id` (positive integer).
5. **Success response:** 200. Example for `GET /api/tickets/57` (history shortened):

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

6. **Error codes:** 400 `INVALID_FORMAT` (id is not a number), 401, 404 `NOT_FOUND` (real example with `/api/tickets/999999`: `"Không tìm thấy phiếu"`, ticket not found).
7. **Notes:** A hidden ticket also returns 404, the same as a ticket that does not exist. An id larger than 9223372036854775807 also returns 404; before, this case made the system return 500, and I fixed it in BUG-006.

### 7. PATCH /api/tickets/{ticket_id}/category

1. **Method and path:** `PATCH /api/tickets/{ticket_id}/category`
2. **Description:** Sets the issue category of a ticket.
3. **Authentication:** Token required; permission `ticket:classify` (NHAN_VIEN only).
4. **Request body:** `category_id` (positive integer, required, must be an existing issue category).

```json
{ "category_id": 1 }
```

5. **Success response:** 200

```json
{ "ticket_id": 61, "category_id": 1, "category_code": "MAN_HINH" }
```

6. **Error codes:** 400 (missing or invalid `category_id`), 401, 403 `FORBIDDEN` (a manager called it), 404 `NOT_FOUND` (real example with category 99999: `"Không tìm thấy loại lỗi"`, category not found; it is also returned when the ticket does not exist).
7. **Notes:** A ticket can be given a new category many times. The system does not keep a history of category changes.

### 8. PATCH /api/tickets/{ticket_id}/technician

1. **Method and path:** `PATCH /api/tickets/{ticket_id}/technician`
2. **Description:** Assigns or changes the technician in charge of a ticket.
3. **Authentication:** Token required; permission `ticket:assign` (NHAN_VIEN only).
4. **Request body:** `technician_id` (positive integer, required; the technician must be active).

```json
{ "technician_id": 2 }
```

5. **Success response:** 200

```json
{ "ticket_id": 61, "status": "MOI", "technician_id": 2, "changed_at": "2026-11-11T17:08:11+07:00" }
```

6. **Error codes:** 400, 401, 403 `FORBIDDEN`, 404 `NOT_FOUND` (`"Không tìm thấy phiếu hoặc kỹ thuật viên"`, ticket or technician not found), 409 `TICKET_CLOSED` (real example: `"Phiếu đã hoàn tất, không thể gán hoặc đổi kỹ thuật viên"`, the ticket is completed).
7. **Notes:** The ticket status does not change when a technician is assigned. Every change of technician is written to the assignment history; choosing the same technician again writes nothing. A deactivated technician cannot be assigned.

### 9. PATCH /api/tickets/{ticket_id}/status

1. **Method and path:** `PATCH /api/tickets/{ticket_id}/status`
2. **Description:** Moves a ticket to the next status.
3. **Authentication:** Token required; permission `ticket:status` (NHAN_VIEN only).
4. **Request body:** `status` (required): `MOI`, `DANG_XU_LY` or `HOAN_TAT`.

```json
{ "status": "DANG_XU_LY" }
```

5. **Success response:** 200

```json
{ "ticket_id": 61, "status": "DANG_XU_LY", "changed_at": "2026-11-11T17:08:11+07:00" }
```

6. **Error codes:** 400 (missing or invalid `status`), 401, 403, 404 `NOT_FOUND`, 409 `INVALID_TRANSITION` (real example when I sent `MOI` for a ticket in progress: `"Sai thứ tự chuyển trạng thái"`, wrong order of status change).
7. **Notes:** The status moves only one way: `MOI` → `DANG_XU_LY` → `HOAN_TAT`. It cannot skip a step or go back. Every change is written to the status history.

### 10. DELETE /api/tickets/{ticket_id}

1. **Method and path:** `DELETE /api/tickets/{ticket_id}`
2. **Description:** Hides a ticket (soft delete). The data is kept, but the ticket no longer appears.
3. **Authentication:** Token required; permission `ticket:delete` (QUAN_LY only).
4. **Path parameter:** `ticket_id`.
5. **Success response:** 200

```json
{ "ticket_id": 61, "deleted_at": "2026-11-11T17:08:12+07:00" }
```

6. **Error codes:** 401, 403 `FORBIDDEN` (real example when a receptionist called it), 404 `NOT_FOUND`.
7. **Notes:** The ticket is not removed from the database. After hiding it, `GET /api/tickets/{id}` returns 404 (I checked this in the real run). The system has no endpoint to restore a hidden ticket.

### 11. GET /api/overview

1. **Method and path:** `GET /api/overview`
2. **Description:** Data for the Overview screen: the number of tickets by status, the number of overdue tickets, the number of tickets due soon, and the five tickets that need the most attention.
3. **Authentication:** Token required; permission `overview:view` (any role).
4. **Parameters:** None.
5. **Success response:** 200. Real example (`attention` shortened to one ticket; at that moment the database also held one test ticket I had created, so `total` is 61):

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

6. **Error codes:** 401, 503.
7. **Notes:** `attention` has at most 5 tickets, with the earliest due dates first. Hidden tickets are not counted.

---

## Group 3. Issue categories, customers, technicians

### 12. GET /api/issue-categories

1. **Method and path:** `GET /api/issue-categories`
2. **Description:** Returns the issue categories used when a ticket is classified.
3. **Authentication:** Token required; permission `ticket:view` (any role).
4. **Parameters:** None.
5. **Success response:** 200 (there are 6 categories; shortened to two)

```json
{ "items": [
  { "category_id": 1, "category_code": "MAN_HINH", "category_name": "Màn hình" },
  { "category_id": 2, "category_code": "PIN", "category_name": "Pin" }
] }
```

The six codes are `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO` and `KHAC`.

6. **Error codes:** 401.
7. **Notes:** This list comes from the sample data and is fixed. The system has no endpoint to add or edit categories.

### 13. GET /api/customers

1. **Method and path:** `GET /api/customers?phone={phone}`
2. **Description:** Looks up a customer by phone number and returns up to the 10 latest tickets of that customer.
3. **Authentication:** Token required; permission `customer:view` (any role).
4. **Query parameter:** `phone` (required). It is normalized the same way as when a ticket is created (accepts `+84`, `84`, spaces and dots), and must then be 10 digits starting with 0.
5. **Success response:** 200. Real example for `GET /api/customers?phone=0969580438`:

```json
{
  "customer_id": 13, "full_name": "Lê Văn Hiếu", "phone": "0969580438",
  "tickets": [
    { "ticket_id": 57, "ticket_code": "BH-000456/2026", "status": "HOAN_TAT",
      "received_at": "2026-08-31T10:45:00+07:00" }
  ]
}
```

6. **Error codes:** 400 `REQUIRED_FIELD_MISSING` (no `phone`), 400 `INVALID_FORMAT` (wrong phone format), 401, 404 `NOT_FOUND` (real example with `0000000000`: `"Không tìm thấy khách hàng"`, customer not found).
7. **Notes:** The search is an exact match on the phone number; it cannot search by name. Each phone number has only one customer record.

### 14. GET /api/technicians

1. **Method and path:** `GET /api/technicians`
2. **Description:** Returns the technicians to choose from when a ticket is assigned.
3. **Authentication:** Token required; permission `technician:view` (any role).
4. **Query parameter:** `include_inactive` (boolean, default `false`). Only QUAN_LY can use it; for NHAN_VIEN it is ignored and only active technicians are returned.
5. **Success response:** 200 (shortened). Real example:

```json
{ "items": [
  { "technician_id": 2, "technician_code": "KT002", "full_name": "Trần Hoài Giang", "is_active": true },
  { "technician_id": 3, "technician_code": "KT003", "full_name": "Đặng Quang Oanh", "is_active": true }
] }
```

When a manager calls `?include_inactive=true`, the list also contains technicians with `"is_active": false` (for example `KT001` and `KT011`).

6. **Error codes:** 401.
7. **Notes:** The sample data has 38 technicians, and 2 of them are deactivated. The list is not paged.

### 15. POST /api/technicians

1. **Method and path:** `POST /api/technicians`
2. **Description:** Adds a new technician.
3. **Authentication:** Token required; permission `technician:manage` (QUAN_LY only).
4. **Request body:**

| Field | Type | Required | Rule |
|---|---|---|---|
| `technician_code` | string | yes | letters, digits, hyphen or underscore, at most 20 characters; converted to upper case |
| `full_name` | string | yes | at most 120 characters |

```json
{ "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử" }
```

5. **Success response:** 201

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử", "is_active": true }
```

6. **Error codes:** 400 (missing or invalid field), 401, 403 `FORBIDDEN` (real example when a receptionist called it), 409 `DUPLICATE_CODE` (real example: `fields: {"technician_code": "Mã này đã được dùng"}`, this code is already used).
7. **Notes:** The technician code must be unique; sending a code that already exists returns 409.

### 16. PATCH /api/technicians/{technician_id}

1. **Method and path:** `PATCH /api/technicians/{technician_id}`
2. **Description:** Edits the name of a technician, or turns the active flag on or off.
3. **Authentication:** Token required; permission `technician:manage` (QUAN_LY only).
4. **Request body:** at least one of the two fields.

| Field | Type | Rule |
|---|---|---|
| `full_name` | string | at most 120 characters |
| `is_active` | boolean | must be `true` or `false` |

```json
{ "full_name": "Kỹ thuật viên thử (đã sửa)" }
```

5. **Success response:** 200

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử (đã sửa)", "is_active": true }
```

6. **Error codes:** 400 `REQUIRED_FIELD_MISSING` (real example when I sent `{}`: `fields: {"body": "Cần ít nhất một trường: full_name hoặc is_active"}`, at least one field is needed), 400 `INVALID_FORMAT`, 401, 403, 404 `NOT_FOUND`.
7. **Notes:** The `technician_code` cannot be changed after the technician is created.

### 17. DELETE /api/technicians/{technician_id}

1. **Method and path:** `DELETE /api/technicians/{technician_id}`
2. **Description:** Deactivates a technician (soft delete).
3. **Authentication:** Token required; permission `technician:manage` (QUAN_LY only).
4. **Path parameter:** `technician_id`.
5. **Success response:** 200

```json
{ "technician_id": 39, "technician_code": "KT-DEMO", "full_name": "Kỹ thuật viên thử (đã sửa)", "is_active": false }
```

6. **Error codes:** 401, 403, 404 `NOT_FOUND`.
7. **Notes:** The technician is not removed, so old tickets still show the technician's name. Calling it again gives the same result. A deactivated technician is no longer in the list to choose from and cannot be assigned to a ticket; to turn the technician on again, use endpoint 16 with `{"is_active": true}`.