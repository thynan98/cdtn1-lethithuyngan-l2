# Mô hình dữ liệu – Hệ thống quản lý phiếu bảo hành (Mekong Mobile, luồng L2)

Sinh viên: Lê Thị Thùy Ngân – 2374802010328 – Track SE

## 1. Danh sách thực thể và nguồn gốc

| Thực thể | Ý nghĩa | Phục vụ yêu cầu |
|---|---|---|
| `customer` | Khách hàng, nhận diện bằng số điện thoại | FR-01, FR-07 (US1, US7), QT-01, QT-02 |
| `technician` | Kỹ thuật viên (là dữ liệu, không phải người dùng) | FR-04 (US3) |
| `issue_category` | 6 loại lỗi của case study | FR-03 (US2) |
| `ticket` | Phiếu bảo hành | FR-01, FR-02, FR-05, FR-06, FR-08, FR-09 |
| `ticket_status_log` | Lịch sử chuyển trạng thái | FR-05 (US4), QT-06 |
| `ticket_assignment_log` | Lịch sử đổi kỹ thuật viên | FR-04 (US3, GWT5) |

## 2. Chi tiết từng thực thể

**customer**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| customer_id | BIGINT | PK | khóa nhân tạo |
| full_name | VARCHAR(120) | NOT NULL | |
| phone | VARCHAR(10) | NOT NULL, UNIQUE | đã chuẩn hóa 10 chữ số bắt đầu bằng 0 (QT-01, QT-02) |
| created_at | TIMESTAMP | NOT NULL | |

**technician**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| technician_id | BIGINT | PK | |
| technician_code | VARCHAR(20) | NOT NULL, UNIQUE | |
| full_name | VARCHAR(120) | NOT NULL | |
| is_active | BOOLEAN | NOT NULL | |

**issue_category**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| category_id | INT | PK | |
| category_code | VARCHAR(20) | NOT NULL, UNIQUE | MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC |
| category_name | VARCHAR(60) | NOT NULL | |
| is_active | BOOLEAN | NOT NULL | thêm loại lỗi mới chỉ là thêm một dòng dữ liệu |

**ticket**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| ticket_id | BIGINT | PK | |
| ticket_code | VARCHAR(20) | NOT NULL, UNIQUE | dạng BH-000231/2026 (NFR-03) |
| customer_id | BIGINT | FK → customer, NOT NULL | |
| technician_id | BIGINT | FK → technician, NULL | chưa gán thì để trống |
| category_id | INT | FK → issue_category, NULL | phân loại sau khi tạo (US2) |
| issue_desc | TEXT | NOT NULL | 10–2000 ký tự |
| priority | VARCHAR(10) | NOT NULL | CAO / TRUNG_BINH / THAP, mặc định TRUNG_BINH |
| status | VARCHAR(12) | NOT NULL | MOI / DANG_XU_LY / HOAN_TAT |
| received_at | TIMESTAMP | NOT NULL | |
| due_date | TIMESTAMP | NOT NULL | sinh theo QT-04 (24/72/120 giờ, bỏ Chủ nhật) |

**ticket_status_log**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| log_id | BIGINT | PK | |
| ticket_id | BIGINT | FK → ticket, NOT NULL | |
| from_status | VARCHAR(12) | NULL | lần đầu tạo phiếu thì trống |
| to_status | VARCHAR(12) | NOT NULL | |
| changed_at | TIMESTAMP | NOT NULL | |

**ticket_assignment_log**

| Cột | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| log_id | BIGINT | PK | |
| ticket_id | BIGINT | FK → ticket, NOT NULL | |
| from_technician_id | BIGINT | FK → technician, NULL | lần gán đầu thì trống |
| to_technician_id | BIGINT | FK → technician, NOT NULL | |
| changed_at | TIMESTAMP | NOT NULL | |

## 3. Quan hệ

- Một `customer` có không hoặc nhiều `ticket`; mỗi `ticket` thuộc đúng một `customer`.
- Một `technician` được gán cho không hoặc nhiều `ticket`; mỗi `ticket` có không hoặc một `technician`.
- Một `issue_category` gắn với không hoặc nhiều `ticket`; mỗi `ticket` có không hoặc một `issue_category`.
- Một `ticket` có không hoặc nhiều dòng trong `ticket_status_log` và `ticket_assignment_log`.
- `ticket_assignment_log` tham chiếu `technician` hai lần (người cũ, người mới).

## 4. Kiểm tra chuẩn 3NF

- Mọi cột không khóa chỉ phụ thuộc vào khóa chính của bảng chứa nó: thông tin khách chỉ ở `customer`, tên kỹ thuật viên chỉ ở `technician`, tên loại lỗi chỉ ở `issue_category`; `ticket` chỉ giữ khóa tham chiếu.
- Không lưu giá trị tính được: "quá hạn" và "sắp đến hạn" do hệ thống tính từ `due_date` và thời điểm hiện tại, không có cột riêng.
- Lịch sử đổi trạng thái và đổi kỹ thuật viên tách thành hai bảng riêng, vì nếu chỉ ghi đè cột `status` hay `technician_id` thì không trả lời được "phiếu ở trạng thái Đang xử lý bao lâu" hay "ai đã xử lý trước đó".
- Không có phi chuẩn hóa có chủ ý.

## 5. Index và yêu cầu phi chức năng

| Index | Phục vụ | Lý do |
|---|---|---|
| `ticket(ticket_code)` UNIQUE | NFR-03 | mã phiếu không trùng |
| `customer(phone)` UNIQUE | QT-01, US7, NFR-01 | tìm khách theo số điện thoại nhanh, không tạo trùng |
| `ticket(status, due_date)` | NFR-04, US6 | lọc danh sách phiếu theo trạng thái và quá hạn |
| `ticket_status_log(ticket_id, changed_at)` | QT-06 | xem lịch sử chuyển trạng thái theo phiếu |
| `ticket_assignment_log(ticket_id, changed_at)` | GWT5 | xem lịch sử đổi kỹ thuật viên |

## 6. Ánh xạ sang MongoDB

Mỗi thực thể thành một collection riêng (không lồng vào nhau); khóa ngoại thành trường số nguyên tham chiếu tới khóa `*_id` của collection kia; việc kiểm tra tham chiếu hợp lệ do lớp nghiệp vụ làm, vì MongoDB không tự kiểm tra khóa ngoại.

| Khái niệm quan hệ | Trong MongoDB |
|---|---|
| Bảng | Collection |
| Khóa chính | Trường số nguyên `*_id` (ví dụ `ticket_id`), có unique index; không dùng ObjectId (khớp quy ước trong `docs/api-contract.md`) |
| Khóa ngoại | Trường tham chiếu (`customer_id`, `technician_id`, …) |
| UNIQUE | Unique index |
| NOT NULL, CHECK | JSON Schema validation |

Khung khai báo (thay cho SQL DDL skeleton):

```javascript
db.createCollection("customer", {
  validator: { $jsonSchema: {
    bsonType: "object",
    required: ["customer_id", "full_name", "phone", "created_at"],
    properties: {
      customer_id: { bsonType: "long" },
      full_name:  { bsonType: "string", maxLength: 120 },
      phone:      { bsonType: "string", pattern: "^0[0-9]{9}$" },   // QT-01, QT-02
      created_at: { bsonType: "date" }
    }
  }}
});
db.customer.createIndex({ customer_id: 1 }, { unique: true });
db.customer.createIndex({ phone: 1 }, { unique: true });

db.createCollection("ticket", {
  validator: { $jsonSchema: {
    bsonType: "object",
    required: ["ticket_id", "ticket_code", "customer_id", "issue_desc", "priority", "status", "received_at", "due_date"],
    properties: {
      ticket_id:     { bsonType: "long" },
      ticket_code:   { bsonType: "string" },
      customer_id:   { bsonType: "long" },
      technician_id: { bsonType: ["long", "null"] },
      category_id:   { bsonType: ["long", "null"] },
      issue_desc:    { bsonType: "string", minLength: 10, maxLength: 2000 },
      priority:      { enum: ["CAO", "TRUNG_BINH", "THAP"] },
      status:        { enum: ["MOI", "DANG_XU_LY", "HOAN_TAT"] },        // QT-06
      received_at:   { bsonType: "date" },
      due_date:      { bsonType: "date" }                                // QT-04
    }
  }}
});
db.ticket.createIndex({ ticket_id: 1 }, { unique: true });
db.ticket.createIndex({ ticket_code: 1 }, { unique: true });           // NFR-03
db.ticket.createIndex({ status: 1, due_date: 1 });                     // NFR-04

db.technician.createIndex({ technician_code: 1 }, { unique: true });
db.issue_category.createIndex({ category_code: 1 }, { unique: true });
db.ticket_status_log.createIndex({ ticket_id: 1, changed_at: 1 });
db.ticket_assignment_log.createIndex({ ticket_id: 1, changed_at: 1 });
```

(Các collection `technician`, `issue_category`, `ticket_status_log`, `ticket_assignment_log` khai báo validator tương tự theo bảng ở mục 2.)

## 7. Phụ lục: SQL DDL skeleton (PostgreSQL)

Dùng khi cần nộp đúng dạng SQL DDL. Đây là bản thiết kế logic, chưa chạy.

```sql
CREATE TABLE customer (
  customer_id BIGSERIAL PRIMARY KEY,
  full_name   VARCHAR(120) NOT NULL,
  phone       VARCHAR(10)  NOT NULL UNIQUE,          -- QT-01, QT-02
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE technician (
  technician_id   BIGSERIAL PRIMARY KEY,
  technician_code VARCHAR(20)  NOT NULL UNIQUE,
  full_name       VARCHAR(120) NOT NULL,
  is_active       BOOLEAN      NOT NULL DEFAULT true
);

CREATE TABLE issue_category (
  category_id   SERIAL PRIMARY KEY,
  category_code VARCHAR(20) NOT NULL UNIQUE,
  category_name VARCHAR(60) NOT NULL,
  is_active     BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE ticket (
  ticket_id     BIGSERIAL PRIMARY KEY,
  ticket_code   VARCHAR(20) NOT NULL UNIQUE,         -- NFR-03
  customer_id   BIGINT NOT NULL REFERENCES customer(customer_id),
  technician_id BIGINT REFERENCES technician(technician_id),
  category_id   INT    REFERENCES issue_category(category_id),
  issue_desc    TEXT   NOT NULL CHECK (length(issue_desc) BETWEEN 10 AND 2000),
  priority      VARCHAR(10) NOT NULL DEFAULT 'TRUNG_BINH'
                  CHECK (priority IN ('CAO','TRUNG_BINH','THAP')),
  status        VARCHAR(12) NOT NULL DEFAULT 'MOI'
                  CHECK (status IN ('MOI','DANG_XU_LY','HOAN_TAT')),   -- QT-06
  received_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  due_date      TIMESTAMPTZ NOT NULL                 -- QT-04
);

CREATE TABLE ticket_status_log (
  log_id      BIGSERIAL PRIMARY KEY,
  ticket_id   BIGINT NOT NULL REFERENCES ticket(ticket_id),
  from_status VARCHAR(12),
  to_status   VARCHAR(12) NOT NULL,
  changed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ticket_assignment_log (
  log_id             BIGSERIAL PRIMARY KEY,
  ticket_id          BIGINT NOT NULL REFERENCES ticket(ticket_id),
  from_technician_id BIGINT REFERENCES technician(technician_id),
  to_technician_id   BIGINT NOT NULL REFERENCES technician(technician_id),
  changed_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ticket_status_due ON ticket(status, due_date);           -- NFR-04
CREATE INDEX idx_status_log_ticket ON ticket_status_log(ticket_id, changed_at);
CREATE INDEX idx_assign_log_ticket ON ticket_assignment_log(ticket_id, changed_at);
```