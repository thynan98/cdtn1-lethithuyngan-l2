"""Tạo bản mẫu nhỏ trong data/sample/ từ bộ dữ liệu đầy đủ của thầy (đặt ở data/raw/).

Chạy:  python tools/make_sample.py
Quy tắc chọn (cố định nên chạy lại ra đúng cùng bản mẫu):
  - lấy 12 phiếu đầu tiên (theo ticket_id) của MỖI trạng thái trong 5 trạng thái lịch sử;
  - chỉ lấy phiếu mà khách hàng có số điện thoại (hệ thống nhận diện khách bằng số điện thoại);
  - giữ toàn bộ 38 kỹ thuật viên và 6 loại lỗi; chỉ giữ khách và nhật ký thuộc 60 phiếu đã chọn.
"""
import csv
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/sample")
PER_STATUS = 12


def read(name):
    with open(RAW / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(name, rows, fields):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    customers = {r["record_id"]: r for r in read("customers_raw.csv")}
    tickets = sorted(read("tickets_history.csv"), key=lambda r: int(r["ticket_id"]))
    chosen, taken = [], {}
    for t in tickets:
        has_phone = customers[t["customer_id"]]["so_dien_thoai"].strip() != ""
        if has_phone and taken.get(t["status"], 0) < PER_STATUS:
            taken[t["status"]] = taken.get(t["status"], 0) + 1
            chosen.append(t)
    ids = {t["ticket_id"] for t in chosen}
    cust_ids = {t["customer_id"] for t in chosen}

    write("tickets_sample.csv", chosen, list(chosen[0].keys()))
    write("customers_sample.csv", [customers[i] for i in sorted(cust_ids, key=int)],
          ["record_id", "ho_ten", "so_dien_thoai", "email", "dia_chi", "ngay_tao"])
    logs = [r for r in read("ticket_status_log.csv") if r["ticket_id"] in ids]
    write("ticket_status_log_sample.csv", logs, list(logs[0].keys()))
    for name in ("technicians.csv", "issue_categories.csv"):
        rows = read(name)
        write(name, rows, list(rows[0].keys()))
    print(f"Đã tạo bản mẫu: {len(chosen)} phiếu, {len(cust_ids)} khách, {len(logs)} dòng nhật ký")


if __name__ == "__main__":
    main()
