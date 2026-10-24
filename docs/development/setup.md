# Perimeter Developer Setup & Troubleshooting Guide

This guide provides deep-dive setup instructions, environment configurations, and debugging procedures for engineers developing or testing **Perimeter**.

---

## 1. Environment Requirements

| Tool | Minimum Version | Recommended | Notes |
| :--- | :--- | :--- | :--- |
| **Python** | 3.12.0 | 3.12.1+ | Ensure `python` and `pip` are in system PATH. |
| **Node.js** | 18.0.0 | 20 LTS or 22 | Required for Vite frontend bundling. |
| **npm** | 9.0.0 | 10+ | Included with Node.js. |
| **Git** | 2.30.0 | Latest | Required for version control and submodules. |

---

## 2. Step-by-Step Local Setup

### 1. Repository Clone & Python Virtual Environment
```bash
git clone https://github.com/vaidzss/perimeter.git
cd perimeter

# Create virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install unified requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Frontend Dependencies Installation
```bash
# Perimeter SOC Dashboard
cd frontend/dashboard
npm install
cd ../..

# BharatPay Neobank Customer Portal
cd frontend/bharatpay/frontend
npm install
cd ../../..
```

### 3. Database Initialization
Perimeter requires the BharatPay SQLite database to be seeded with initial user accounts, merchant registries, and organizational hierarchies:

```bash
python frontend/bharatpay/seed/seed.py
```

---

## 3. Launching Services Individually

Perimeter consists of four coordinated microservices:

| Service | Port | Directory | Launch Command |
| :--- | :--- | :--- | :--- |
| **BharatPay Backend** | `8001` | `frontend/bharatpay/backend` | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8001` |
| **Perimeter Security Gateway** | `8000` | Repository root | `python -m uvicorn person1_api_discovery.app.main:app --host 0.0.0.0 --port 8000` |
| **Perimeter SOC Console** | `3000` | `frontend/dashboard` | `npm run dev` |
| **BharatPay Portal** | `5173` | `frontend/bharatpay/frontend` | `npm run dev` |

---

## 4. Running Verification & Demonstration Scripts

### Active Defense Verification Suite
Verifies all 4 active defense assertions (In-Flight PII Redaction, Route Quarantine, IP Blacklisting, Clean Business Continuity):
```bash
python verify_perimeter_defense.py
```

### Before-and-After Attack Demonstration
Executes side-by-side attacks against the unprotected target service and through Perimeter:
```bash
python demo_before_after.py
```

### Automated Unit & Integration Tests
Runs all 130 tests across all modules:
```bash
python -m pytest
```

---

## 5. Troubleshooting & FAQ

### Port Conflicts (8000, 8001, 3000, 5173)
If a previous run left processes listening on required ports, run the clean shutdown script:

```powershell
# Windows PowerShell
.\stop_all.ps1
```

Or inspect manually:
```powershell
Get-NetTCPConnection -LocalPort 8000, 8001, 3000, 5173 | Format-Table OwningProcess, LocalPort, State
```

### Empty Database or Missing Employee Norms
If tests in `frontend/bharatpay/backend/tests` report `assert len(employees) >= 12` failure:
Run the seed script:
```bash
python frontend/bharatpay/seed/seed.py
```
