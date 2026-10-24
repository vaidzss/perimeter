# BharatPay — Fictional Neobank & UPI Target System
> **Target Neobank & Vulnerable API Testbed for Perimeter ASPM & Inline Active Defense**  
> *Notice: All accounts, balances, Aadhaar, PAN, and transactions in this application are 100% synthetic test data.*

---

## 🏛️ Architecture Overview
BharatPay represents a modern Indian fintech application designed with calm, authentic aesthetics (Inter font, soft elevation, unified brand accent, integer paise accounting). Behind the scenes, it serves as the deliberately vulnerable target testbed for API security posture management:

- **Reverse Proxy / API Gateway**: Nginx on Port `80` emitting structured JSON gateway logs (`./logs/nginx_access.log`) with request timings and upstream latency.
- **Backend API**: Python FastAPI on internal port `8000` with SQLite + SQLAlchemy, PyJWT authentication, and custom structured request telemetry (`./logs/requests.jsonl` and `requests` table).
- **Frontend App**: React 18 + Vite + TypeScript + Tailwind CSS with a persistent synthetic watermark and hidden red-team simulation drawer (`Shift + R`).

---

## 📂 Deliverables & Repository Layout
```text
/bharatpay
  ├── backend/          # FastAPI server, SQLAlchemy models, logging middleware
  │   ├── app/          # Core routers (v2 documented, v1 zombie, internal shadow)
  │   └── tests/        # 31 automated tests covering auth, banking, logging, attacks
  ├── frontend/         # React customer dashboard & Red-Team Drawer (Shift + R)
  ├── nginx/            # Reverse proxy configuration with gateway JSON logging
  ├── seed/             # Synthetic seed script (18 users, 356 merchants, 300+ txns)
  ├── spec/
  │   ├── openapi.json  # Intentionally partial OpenAPI spec (4 public routes only)
  │   ├── sample_logs.jsonl # 200+ real labeled logs (benign + all 3 attack scenarios)
  │   └── schema.md     # Complete JSON telemetry schema documentation
  ├── docker-compose.yml# Multi-service stack (Nginx + Backend + Frontend + Logs)
  ├── VULNERABILITIES.md# Ground truth flaw registry (CVSS scores, mechanics, IOCs)
  ├── smoke_test.py     # End-to-end automated verification script
  ├── run.sh / run.ps1  # Local development launchers (Linux / Windows)
  └── README.md
```

---

## 🚀 Cold Start Quickstart

### Option 1: Full Docker Compose (Recommended for Hackathon Presentation)
```bash
cd bharatpay
docker compose up --build
```
- Open `http://localhost/` in your browser.
- All incoming traffic routes through Nginx port 80.
- Gateway logs are written directly to `./logs/nginx_access.log`.
- Structured application logs are written to `./logs/requests.jsonl`.

### Option 2: Local Development Mode
- **Windows**:
  ```powershell
  cd bharatpay
  .\run.ps1
  ```
- **Linux / macOS**:
  ```bash
  cd bharatpay
  ./run.sh
  ```

---

## 👥 Seeded Test Credentials

All test accounts use the password: `Password@123` (or test OTP stub `123456`).

| Name | Role | Email | Mobile | UPI VPA | Balance | KYC Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Priya Sharma** | Primary Demo User | `priya.sharma@bharatpay.com` | `9876501001` | `priya.sharma@bharatpay` | ₹48,500.00 | Verified |
| **Rohit Verma** | High-Balance User | `rohit.verma@bharatpay.com` | `9876501002` | `rohit.verma@bharatpay` | ₹1,25,000.00 | Verified |
| **Ananya Iyer** | Pending KYC User | `ananya.iyer@bharatpay.com` | `9876501003` | `ananya.iyer@bharatpay` | ₹18,200.00 | Pending |
| *+ 15 additional seeded users* | Customer accounts | ... | ... | ... | ₹8,400–₹2,10,000 | Verified |

---

## 🎯 How Person 1 & 2's Pipeline Connects

### 1. For Person 1: API Discovery & Shadow API Detection
- **Ground Truth Catalog**: Point your catalog comparator at [`spec/openapi.json`](spec/openapi.json). This file documents only the 4 public routes.
- **Log Feeds to Ingest**:
  - Gateway Log: `./logs/nginx_access.log` (JSON format with `$request_uri`, `$status`, `$upstream_response_time`).
  - Application Telemetry: `./logs/requests.jsonl` (contains `path_template` and `raw_path`).
- **Shadow Detection Goal**: When traffic hits the application, diffing observed paths against `openapi.json` will accurately flag:
  1. `GET /api/v1/kyc/aadhaar-pan-dump` -> **Undocumented Zombie Endpoint**
  2. `POST /api/internal/debug/override-limit` -> **Undocumented Shadow Backdoor**

### 2. For Person 2: Threat Detection & Abuse Prevention
- **Telemetry Feed**: Ingest `./logs/requests.jsonl` or query SQLite `requests` table.
- **Attack 1 (BOLA/IDOR)**: Correlate requests having identical `token_id` or `user_id` across diverse `object_ids` (`1002`, `1003`, ..., `1050`) within short time windows with 403 status codes.
- **Attack 2 (Scraping & Exfiltration)**: Detect velocity spikes (> 50 req/sec) and `sensitive_types: ["pan", "aadhaar"]` on unauthenticated routes.
- **Attack 3 (Token Replay / Botnet Hijacking)**: Detect identical `token_id` (`jti`) used concurrently across differing `client_ip` (`185.220.101.5` Tor exit) and non-browser `user_agent` (`python-requests/2.31.0`).

---

## 🛑 Live Demo Presentation Script

1. **Step 1: The Legitimate Neobank Experience**
   - Navigate to `http://localhost/` and log in as Priya Sharma (`priya.sharma@bharatpay.com` / `Password@123`).
   - Show dashboard: account balance ₹48,500.00, masked PAN (`ABCDE****F`), and last 10 transactions.
   - Go to **Send Money**, transfer ₹250 to `swiggy@bharatpay`. Show instant balance deduction.
   - Show **Merchant Directory**: search for "Swiggy", show 350+ verified brands.

2. **Step 2: Triggering Attack Scenarios via Red-Team Drawer**
   - Press <kbd>Shift</kbd> + <kbd>R</kbd> (or click *"Red Team Simulation"* in footer).
   - **Click "Enumerate Accounts #1002–#1050"**: Show live probe counter reaching 48 accounts. Point to Sentinel dashboard detecting BOLA horizontal sweep.
   - **Click "Scrape Merchant & KYC Directory"**: Show live harvest counter capturing unmasked records from zombie endpoint. Point to Sentinel detecting Zombie API exfiltration.
   - **Click "Replay Token from Botnet IP"**: Point to Sentinel alert for Token Misuse (same `jti`, Tor exit IP).

3. **Step 3: Reset Demo State**
   - In the drawer, click **"Reset Demo State"** to restore account balances and daily limits for the next round of judging.
