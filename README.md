# Perimeter (CC6-IC07)
## Autonomous API Security Posture Management (ASPM) & Inline Threat Neutralization Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0-61dafb.svg)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5.0-646cff.svg)](https://vitejs.dev)
[![Accuracy](https://img.shields.io/badge/Detection%20TPR-94.7%25-brightgreen.svg)]()
[![Precision](https://img.shields.io/badge/False%20Positive%20Rate-0.0%25-brightgreen.svg)]()
[![Latency](https://img.shields.io/badge/Inspection%20Latency-%3C2.0ms-success.svg)]()

---

## 🛡️ What is Perimeter?

**Perimeter** is an enterprise-grade, zero-instrumentation **API Security Posture Management (ASPM)** and **Inline Active Defense Platform**. Designed for modern cloud-native FinTech and microservice architectures, Perimeter detects and mitigates the #1 OWASP API vulnerability—**Broken Object Level Authorization (BOLA/IDOR)**—uncovers uncataloged **Shadow & Zombie APIs**, monitors **OpenAPI specification drift**, redacts sensitive Indian PII in-flight (`9999-XXXX-1001`, `ABCDE****F`), and deploys **autonomous zero-downtime virtual patches**.

---

## 🌟 Key Capabilities

### 1. In-Flight API Discovery & Spec Reconciler (Person 1)
* **Zero-Code Instrumentation:** Operates as an inline reverse proxy on Port `8000`. No SDKs, bytecode manipulators, or microservice code modifications required.
* **Continuous Inventory & Drift Detection:** Automatically compares live traffic against governed OpenAPI v3.1 specs, categorizing routes into **Documented**, **Shadow**, **Zombie (Deprecated)**, and **Unused**.
* **Auto-Swagger Synthesizer:** Automatically generates compliant OpenAPI 3.1 definitions for newly discovered shadow endpoints with 1 click.

### 2. AI & Mathematical Detection Engine (Person 2)
* **URL Parameterizer (Box A):** Groups dynamic high-cardinality paths (e.g. `/api/v2/accounts/1004/statement`) into standardized templates.
* **Online Statistical Profiling (Box B):** Computes numerically stable online variance and mean using **Welford’s Algorithm** ($O(1)$ time and memory), detecting abnormal velocity spikes and horizontal object sweeps.
* **Actor Attribution & Confusion Matrix (Box C):** Evaluates risk scores ($0 - 100$) in real-time, maintaining verified performance (**94.7% TPR, 0.0% FPR**).

### 3. Inline Active Defense & Virtual Patching
* **Route Quarantine Virtual Patching:** Instantly drops attacks targeting uncataloged shadow backdoors and zombie KYC endpoints with `HTTP 403 Forbidden` (`ROUTE_QUARANTINED_BY_PERIMETER`).
* **IP Quarantine:** Drops malicious Tor exit nodes and automated credential-replay botnets at the perimeter edge (`HTTP 403 Forbidden` / `IP_QUARANTINED_BY_PERIMETER`).
* **In-Flight Data Sanitizer:** Intercepts raw Aadhaar and PAN numbers in transit and redacts them before wire transmission, ensuring full compliance with the **Digital Personal Data Protection (DPDP) Act 2023** and **RBI Master Directions**.
* **Zero Customer Disruption:** Legitimate banking users (Priya Sharma on `GET /api/v2/auth/me` and `/api/v2/upi/merchants`) experience **100% uninterrupted business continuity**.

### 4. Enterprise SOC Command Center Console
* Real-time React 18 + Vite dashboard featuring live Security Posture Scores, active threat alert triage, forensic cURL inspectors, lateral movement graphs, and an **Allowed vs. Blocked Live Resolutions Table**.

---

## 📚 Complete Technical Documentation (`/docs`)

Comprehensive documentation is available in the [`docs/`](docs/) directory:

* **[Executive Overview & Problem Statement](docs/overview.md):** The "Shadow Surface Dilemma", OWASP API Top 10 vulnerabilities, and core value proposition.
* **[System Architecture & Technical Specs](docs/architecture.md):** Decoupled microservice topology, Mermaid request lifecycles, and component specifications.
* **[Feasibility, Performance & Compliance Analysis](docs/feasibility.md):** Sub-2ms latency profile, Welford $O(1)$ complexity, economic ROI, and DPDP / RBI compliance.
* **[Red-Team Cyberattack & Simulation Guide](docs/simulation.md):** Multi-vector cyberattack simulation, step-by-step reproduction guide, and before-vs-after verification matrix.
* **[REST API Reference](docs/api_reference.md):** Full documentation of Perimeter Control-Plane and Ingress Gateway endpoints, payloads, and WebSocket streams.

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
* Windows, Linux, or macOS.
* Python 3.12+ installed.
* Node.js 18+ and npm installed.

### 1. Launch Services

#### Terminal 1: BharatPay Core Banking Backend (Port 8001)
```powershell
cd frontend\bharatpay\backend
..\..\..\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

#### Terminal 2: Perimeter Security Gateway (Port 8000)
```powershell
.\venv\Scripts\python.exe -m uvicorn person1_api_discovery.app.main:app --host 0.0.0.0 --port 8000
```

#### Terminal 3: Perimeter SOC Command Center (Port 3000)
```powershell
cd frontend\dashboard
npm run dev
```

#### Terminal 4: BharatPay Customer Web Portal (Port 5173)
```powershell
cd frontend\bharatpay\frontend
npm run dev
```

---

## 🎮 Live Demonstration & Test Scripts

Run the automated simulation scripts in the repository root:

```powershell
# 1. Comprehensive Before-and-After Live Demonstration
.\venv\Scripts\python.exe demo_before_after.py

# 2. Automated Active Defense Verification Suite (4/4 Assertions)
.\venv\Scripts\python.exe verify_perimeter_defense.py

# 3. Red-Team Attack Telemetry Generator
.\venv\Scripts\python.exe simulate_bharatpay_attack.py
```

---

## 🌐 Live URLs

* **Perimeter SOC Dashboard:** [http://localhost:3000](http://localhost:3000)
* **Perimeter Gateway & API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **BharatPay Banking Portal:** [http://localhost:5173](http://localhost:5173)
* **BharatPay Target API:** [http://localhost:8001/health](http://localhost:8001/health)

---

## 📂 Repository Directory Layout

```
perimeter/
├── README.md                      # Project Overview & Quickstart Navigator
├── demo_before_after.py           # Live Before vs After Demonstration Script
├── verify_perimeter_defense.py    # Active Defense Automated Test Suite (4/4 Passed)
├── simulate_bharatpay_attack.py   # Red-Team Attack Simulation Script
├── seed_demo_traffic.py           # Demo Traffic Generator
├── requirements.txt               # Unified Python Dependencies
│
├── docs/                          # Comprehensive Technical Documentation
│   ├── README.md                  # Documentation Hub Index
│   ├── overview.md                # Problem Statement & Executive Overview
│   ├── architecture.md            # Topology, Sequence Diagrams & Lifecycles
│   ├── feasibility.md             # Sub-2ms Latency, Welford O(1), DPDP/RBI Compliance
│   ├── simulation.md              # 4 Attack Vectors, Red-Team & Defense Guide
│   └── api_reference.md           # Full REST API Reference & WebSocket Specs
│
├── person1_api_discovery/         # Person 1: Gateway & Discovery Platform
│   ├── app/
│   │   ├── gateway.py             # Reverse-Proxy & Active Defense Interceptor
│   │   ├── inventory_service.py   # Spec Reconciler, Drift & Quarantine Service
│   │   ├── middleware.py          # Fast Telemetry & In-Flight PII Streamer
│   │   ├── normalizer.py          # Dynamic URL Normalizer & Regex Matcher
│   │   ├── person2_bridge.py      # Multi-Spec Indexer & WebSocket Bridge
│   │   ├── main.py                # FastAPI Application & Ingress Gateway (:8000)
│   │   └── routers/               # Defense, Inventory, Dashboard Compat Routers
│   └── specs/                     # Governed OpenAPI v3 Specifications
│
├── traffic-detection-engine/      # Person 2: AI & Mathematical Detection Engine
│   ├── core/                      # Box A (Parameterizer), Box B (Welford), Box C (Actor)
│   ├── pipeline.py                # Detection Pipeline & Telemetry Processor
│   └── server.py                  # Standalone Engine Server
│
└── frontend/
    ├── dashboard/                 # Perimeter React 18 SOC Command Center (:3000)
    │   ├── src/
    │   │   ├── pages/             # Overview, Inventory, Alerts, Investigations, Defense
    │   │   ├── api/               # React Query Hooks & API Client
    │   │   └── components/        # Tables, Recharts Velocity Graphs, Metric Cards
    │   └── package.json
    │
    └── bharatpay/                 # Target FinTech Banking Application
        ├── backend/               # BharatPay Core API (:8001 - FastAPI + SQLite)
        ├── frontend/              # BharatPay Customer Portal (:5173 - React/Vite)
        └── spec/                  # BharatPay Documented OpenAPI Specification
```

---

## 🔒 Security & Data Privacy Standard

* **Zero Plaintext Secrets:** All sensitive credentials and configuration keys are managed strictly via `.env` files.
* **Strict Synthetic Data Standard:** All demonstration scripts, seed data, and tests utilize purely synthetic test identifiers (`Priya Sharma`, `[GOVT-ID-XXXX-XXXX]`, `ABCDE1234F`). No genuine citizen or banking data is stored or processed.
