-- schema.sql - SQL DDL skeleton (PostgreSQL), Mekong Mobile luong L2 "Yeu cau bao hanh"
-- Day la ban thiet ke logic. He thong thuc te luu tru bang MongoDB,
-- xem docs/data-model.md (muc 6) de biet anh xa sang collection.

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