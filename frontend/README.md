# Perimeter SOC Command Center & Target Neobank
## Autonomous API Security Posture Management & Active Threat Neutralization

A full-stack, enterprise-grade API Security Posture Management (ASPM) platform and active defense system designed for modern microservice environments. 

Perimeter detects the #1 OWASP API vulnerability—**Broken Object Level Authorization (BOLA/IDOR)**—uncovers uncataloged **Shadow & Zombie APIs**, monitors **OpenAPI specification drift**, inspects raw HTTP forensics, and executes **autonomous zero-downtime virtual patching**.

---

## 🌟 Key Capabilities & Dashboard Views

1. **Security Posture & Overview (`/`)**
   - Live Security Posture Score dial (0-100, Grade A to F) with category breakdowns.
   - High-level KPIs: Monitored APIs (142), Shadow APIs (18), Active Critical Threats, Blocked Attacks 24h, Sensitive Data Exposures (26).
   - OWASP API Security Top 10 (2023) vulnerability breakdown (Recharts BarChart).
   - 7-Day Threat & Posture score trajectory (Recharts AreaChart).
   - Origin threat infrastructure & ASN breakdown.

2. **Searchable API Inventory (`/inventory`)**
   - Real-time catalog of all endpoints across services and hosts.
   - Multi-dimensional filters: Fuzzy search by path/service/PII, HTTP Method (GET, POST, PUT, DELETE, PATCH), Status (Managed, Shadow, Zombie, Deprecated), and Risk Score slider.
   - Visual badges for auth guards, detected PII (SSN, credit card, bank account), and OpenAPI spec drift.

3. **API Detail & Risk Breakdown Modal**
   - Granular vulnerability scoring mapped to OWASP API Top 10.
   - Inspected parameter matrix (Path, Query, Headers, Body with data sensitivity tags).
   - Live OpenAPI specification drift detector highlighting undocumented fields (e.g. `?include_raw_records=true`).
   - Raw request & response sample viewer with unmasked PII warnings.
   - Recommended engineering remediation guidance & 1-click **Zero-Downtime Virtual Patching**.

4. **Threat Alerts List (`/alerts`)**
   - Real-time stream of security incidents with pulsing severity indicators.
   - Rich metadata: Target endpoint, Threat Actor IP, Geo country, JA3/JA4 TLS fingerprints, blast radius.
   - Direct 1-click drill-down to the **Investigation View**.

5. **Traffic Analytics (`/traffic`)**
   - Ingress throughput time-series: Clean baseline vs Malicious anomaly spikes (Recharts AreaChart).
   - Latency impact profile: P50 vs P95 latency (sub-1.2ms inspection overhead).
   - HTTP response status code breakdown (200, 201, 400, 401, 403 Blocked, 429 Rate-Limited, 500).
   - Top aggressive actors table with 1-click **Global IP Blocking**.

6. **Forensic Investigation Workbench (`/investigation`)**
   - **Attacker Intelligence Dossier:** Source IP, Geo, ISP, ASN, Reputation Score (98/100 Malicious Bot), JA3/JA4 TLS fingerprints, and headless Python User-Agent.
   - **Chronological Incident Reconstruction:** 5-phase attack replay (Reconnaissance → Shadow Route Fingerprinting → First BOLA Manipulation → Scripted Mass Exfiltration → Behavioral Mitigation).
   - **Raw HTTP Inspector & Payload Forensics:** Complete request headers, query parameters, response headers, response body, flagged anomalies, and 1-click **Copy as cURL**.
   - **Actor Global Blast Radius & Lateral Activity:** Comprehensive audit trail of every other microservice probed or exploited by this actor during the session.

7. **Deliverables in Dashboard & Project:**
   - **Interactive Pitch Deck (`/pitch`):** Full 10-slide investor & judge presentation inside the dashboard (also formatted in [PITCH_DECK.md](PITCH_DECK.md)).
   - **5-Minute Live-Attack Demo Script (`/demo`):** Director's cue sheet with exact minute-by-minute talking points, clickable demo triggers, and backup terminal commands (also formatted in [LIVE_ATTACK_DEMO_SCRIPT.md](LIVE_ATTACK_DEMO_SCRIPT.md)).

---

## 🚀 Quickstart & Running Locally

### 1. Backend REST API Server (Port 5000)
```bash
cd backend
npm install
node server.js
```
The REST API runs on `http://localhost:5000`:
* `GET /api/v1/health`
* `GET /api/v1/overview/posture`
* `GET /api/v1/inventory`
* `GET /api/v1/inventory/:id`
* `GET /api/v1/alerts`
* `GET /api/v1/alerts/:id`
* `GET /api/v1/analytics/traffic`
* `GET /api/v1/investigation/:alertId`
* `POST /api/v1/actions/block-actor`
* `POST /api/v1/actions/quarantine-api`
* `POST /api/v1/actions/mitigate-alert`
* `POST /api/v1/simulate-attack`

### 2. Frontend React SOC Console (Port 3000)
```bash
cd dashboard
npm install
npm run dev
```
Open your browser to `http://localhost:3000`.

---

## 🔄 Dual Operation Mode: Live REST API vs Mock Mode
The dashboard features an instant toggle in the top navbar:
* **Live REST API Mode (Default):** Communicates directly with the Express REST API via Vite proxy (`/api/v1`).
* **Mock JSON Mode:** Uses embedded schema-compliant mock fixtures, enabling offline execution and disconnected judge presentations.
* **Automatic Fallback:** If the backend is temporarily unreachable, the frontend automatically falls back to mock data and recovers when the API comes back online.

---

## 📂 Project Structure
```
D:\CYBERCUP PROJECT\
├── PITCH_DECK.md                  # Executive Pitch Deck Presentation
├── LIVE_ATTACK_DEMO_SCRIPT.md     # 5-Minute Live-Fire Attack Demo Script
├── README.md                      # Platform Documentation
├── backend/                       # Real Express REST API Server
│   ├── server.js                  # REST Endpoints, Simulation Engine, In-memory DB
│   └── package.json
└── dashboard/                     # React + Vite + Tailwind 4 + Recharts Frontend
    ├── src/
    │   ├── types/apiSecurity.ts   # TypeScript interfaces matching all schemas
    │   ├── data/mockData.ts       # Mock fixtures matching all schemas
    │   ├── services/apiService.ts # REST API Client with fallback & actions
    │   ├── components/
    │   │   ├── Navbar.tsx         # Connection status, mock toggle, attack simulator
    │   │   ├── Sidebar.tsx        # Navigation tabs & status indicators
    │   │   ├── OverviewView.tsx   # Posture score gauge, OWASP Top 10, trend chart
    │   │   ├── InventoryView.tsx  # Searchable & filterable API catalog
    │   │   ├── ApiDetailModal.tsx # Risk breakdown, drift inspector, virtual patch
    │   │   ├── AlertsView.tsx     # Security incident stream & triage
    │   │   ├── TrafficAnalyticsView.tsx # Throughput, latency percentiles, top actors
    │   │   ├── InvestigationView.tsx    # Forensic drill-down, timeline, raw HTTP, lateral scope
    │   │   ├── PitchDeckView.tsx  # Slide deck viewer inside dashboard
    │   │   └── LiveDemoScriptView.tsx   # 5-minute cue sheet with runnable triggers
    │   ├── App.tsx
    │   ├── main.tsx
    │   └── index.css
    ├── vite.config.ts             # Tailwind 4 plugin & API proxy to port 5000
    └── package.json
```
