# Perimeter Documentation Hub

Welcome to the comprehensive technical documentation for **Perimeter** (Project CC6-IC07: Autonomous API Security Posture Management & Active Threat Neutralization Platform).

---

## 📚 Documentation Index

| Document | Description |
| :--- | :--- |
| **[Executive Overview](overview.md)** | Problem statement, the "Shadow Surface Dilemma", OWASP API Top 10 vulnerabilities, and core value proposition. |
| **[System Architecture](architecture.md)** | End-to-end topology, Mermaid sequence diagrams, inline gateway lifecycle, and component breakdowns (BharatPay, Person 1, Person 2, SOC Console). |
| **[Feasibility & Compliance](feasibility.md)** | Sub-2ms latency benchmarking, Welford's $O(1)$ statistical profiling, economic ROI, and DPDP Act 2023 / RBI regulatory compliance analysis. |
| **[Simulation & Defense Guide](simulation.md)** | Comprehensive 8-scenario red-team cyberattack simulation guide covering OWASP API Top 10, deep payload & SSRF inspection, supply-chain guard, interactive attacker drawer, and Poisson threat simulator. |
| **[Identity & Access Governance](identity_access.md)** | Enterprise RBAC hierarchy, 6 privileged roles, jurisdiction-enforced reporting, sanctioned business campaign multipliers, and reasoning chains. |
| **[Context-Aware Session Graphing](session_graphing.md)** | Stateful Directed Acyclic Graphs (DAGs) per session, skip-step business flow violation detection (OWASP API6:2023), and Shannon branching entropy reconnaissance detection. |
| **[REST API Reference](api_reference.md)** | Complete technical documentation of all Perimeter Control-Plane and Ingress Gateway endpoints, payloads, and WebSocket streams. |

---

## ⚡ Quickstart Navigation

### 1. Launch All Services
```powershell
# 1. Start BharatPay Core Banking Backend (Port 8001)
cd frontend\bharatpay\backend
..\..\..\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 2. Start Perimeter Security Gateway (Port 8000)
cd ..\..\..
.\venv\Scripts\python.exe -m uvicorn person1_api_discovery.app.main:app --host 0.0.0.0 --port 8000

# 3. Start Perimeter SOC Console (Port 3000)
cd frontend\dashboard
npm run dev

# 4. Start BharatPay Customer Portal (Port 5173)
cd ..\bharatpay\frontend
npm run dev
```

### 2. Live URLs
* **Perimeter SOC Dashboard:** [http://localhost:3000](http://localhost:3000)
* **Perimeter Security Gateway & API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **BharatPay Banking Web Portal:** [http://localhost:5173](http://localhost:5173)
* **BharatPay Core API:** [http://localhost:8001/health](http://localhost:8001/health)

### 3. Run Live Attack & Defense Demonstrations
```powershell
# Run the complete before-and-after attack & active defense demonstration
.\venv\Scripts\python.exe demo_before_after.py

# Run the 4-part automated defense assertion suite
.\venv\Scripts\python.exe verify_perimeter_defense.py

# Run red-team telemetry simulation
.\venv\Scripts\python.exe simulate_bharatpay_attack.py
```
