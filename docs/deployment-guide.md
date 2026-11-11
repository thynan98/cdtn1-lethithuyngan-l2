# Deployment Guide - Mekong Mobile Warranty Ticket System (flow L2)

This guide explains how to run the system on a clean machine with two commands.
I tested it on Windows with Docker Desktop; where the commands differ on macOS/Linux, both versions are given.

## 1. Requirements

- Git
- Docker Desktop (includes Docker Compose v2). It must be running ("Engine running") before you start.
- Free TCP port 8000 on the host. Port 27017 is used only inside the Docker network.
- Internet access for the first build (Docker downloads the `python:3.14-slim` and `mongo:7` images and the Python packages).
- A modern web browser.

You do not need to install Python or MongoDB: both run inside containers.

## 2. Setup steps

1. Get the code (tag `v1.0`):

   ```
   git clone --branch v1.0 https://github.com/thynan98/cdtn1-lethithuyngan-l2.git
   cd cdtn1-lethithuyngan-l2
   ```

2. Create the environment file (first command):

   ```
   cp .env.example .env
   ```

   On Windows PowerShell use `Copy-Item .env.example .env`.

3. Build and start (second command):

   ```
   docker compose up -d --build
   ```

4. Wait about 40 seconds, then check the status:

   ```
   docker compose ps
   ```

   Both services (`mongo` and `app`) must show `(healthy)`.

5. Open http://localhost:8000 in the browser.

To stop the system: `docker compose down`.
To stop and also delete the database volume: `docker compose down -v` (the sample data is loaded again on the next start).

## 3. Environment variables

The variables are listed in `.env.example`. Docker Compose reads `.env` from the project folder.

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `JWT_SECRET` | Yes | none | Secret key used to sign login tokens. At least 32 characters. The application refuses to start without it, and `docker compose up` stops with the message "Thiếu JWT_SECRET" if `.env` is missing. |
| `MONGODB_URI` | Python run only | `mongodb://localhost:27017` | MongoDB connection string. With Docker, `docker-compose.yml` sets it to `mongodb://mongo:27017`, so the value in `.env` is not used. |
| `MONGODB_DB` | No | `warranty` | Database name. With Docker it is fixed to `warranty` by `docker-compose.yml`. |
| `JWT_EXPIRE_MINUTES` | No | `480` | Token lifetime in minutes (8 hours). With Docker the default is used. |
| `LOG_LEVEL` | No | `INFO` | Log level: DEBUG, INFO, WARNING or ERROR. With Docker it is fixed to `INFO`. |

Security note: the `JWT_SECRET` value in `.env.example` is only a sample and it is public in the repository. It is fine for a local trial. For any real deployment, generate your own key and put it in `.env`:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

The `.env` file is ignored by Git and must never be committed.

## 4. Sample data

The sample data is a small simulated data set based on the Mekong Mobile case study (in `data/sample/`). It is loaded automatically every time the `app` container starts (migration, then seed). Running the seed again does not duplicate data.

After the first start the database contains:

| Collection | Records |
|---|---|
| Fault categories | 6 |
| Technicians | 38 |
| User accounts | 2 |
| Customers | 60 |
| Warranty tickets | 60 |

Demo accounts:

| Username | Password | Role |
|---|---|---|
| `nhanvien01` | `NhanVien@2026` | Receptionist: creates, classifies and assigns tickets and changes ticket status. Cannot delete tickets. |
| `quanly01` | `QuanLy@2026` | Manager: views tickets, customers and the overview, hides (soft-deletes) tickets and manages technicians. Cannot create tickets or change their status. |

Both roles can view tickets, customers, technicians and the overview. A request that the role is not allowed to make gets HTTP 403.

To run the seed again by hand and check that nothing is duplicated:

```
docker compose exec app python -m seeds.seed
```

Every collection should report `thêm 0` (Vietnamese for "added 0").

## 5. Verify it works

1. Containers are healthy:

   ```
   docker compose ps
   ```

   Expected: `mongo` and `app` both show `Up ... (healthy)`.

2. The health endpoint answers:

   ```
   curl.exe http://localhost:8000/health
   ```
   On macOS/Linux use `curl http://localhost:8000/health`.
   
   Expected: HTTP 200 and the body `{"status":"ok","db":"ok"}`.

3. Log in at http://localhost:8000 with `nhanvien01` / `NhanVien@2026`. The Overview screen shows 60 tickets split by status, with the number of overdue and nearly due tickets.

4. Open "Danh sách phiếu" (ticket list): a table of tickets with codes like `BH-000604/2026`.

5. Open http://localhost:8000/docs: the interactive API page lists the `/api/...` endpoints.

6. (Optional, needs Python 3.14 and `pip install -r requirements.txt`) run the automated tests:

   ```
   python -m pytest -q
   ```

   Expected: `68 passed`.

## Enabling HTTPS for a real deployment

The application itself serves plain HTTP on port 8000 (`uvicorn`). This is fine for a local trial, but logins and tokens must not travel over plain HTTP on a real server. I have not deployed the system on a public server, so the steps below describe what to do and are not tested here.

1. Put a reverse proxy that handles TLS (for example Caddy or Nginx) in front of the `app` container, and get a certificate for your domain (for example from Let's Encrypt).
2. Let only the proxy listen on the public ports 80 and 443. Remove the `ports: "8000:8000"` line for `app` in `docker-compose.yml`, so that port 8000 is reachable only from the proxy inside the Docker network. MongoDB already publishes no port.
3. Redirect HTTP to HTTPS in the proxy configuration.
4. Replace the sample `JWT_SECRET` with your own random key (see "Environment variables").
5. After the change, open the site with `https://` and check that the browser shows a valid certificate.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `required variable JWT_SECRET is missing` | The `.env` file does not exist. Run `cp .env.example .env` and start again. |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | Another program or container uses port 8000. Stop it (`docker ps` shows containers; `docker compose down` in the other project), then run `docker compose up -d --build` again. |
| `error during connect ... dockerDesktopLinuxEngine` | Docker Desktop is not running. Open it, wait for "Engine running", and retry. |
| `app` is missing from `docker compose ps`, and `docker compose logs app` shows "Temporary failure in name resolution" | A temporary Docker network problem at startup. Run `docker compose down`, then `docker compose up -d --build`. |
| Browser shows "connection refused" | The `app` container is still starting. Wait until `docker compose ps` shows `(healthy)`. |