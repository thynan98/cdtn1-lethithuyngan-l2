# Đóng gói ứng dụng (FastAPI + giao diện tĩnh). Cơ sở dữ liệu chạy ở container "mongo" (xem docker-compose.yml).
FROM python:3.14-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Dựng collection, nạp dữ liệu mẫu (chạy lại không nhân đôi), rồi mở máy chủ.
CMD ["sh", "-c", "python -m migrations.migrate && python -m seeds.seed && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
