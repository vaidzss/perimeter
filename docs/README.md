# Perimeter Documentation Hub

Welcome to the comprehensive technical documentation for **Perimeter** (Autonomous API Security Posture Management & Active Threat Neutralization Platform).

---

## 📚 Documentation Index

### Core Architecture & Platform Guides
| Document | Description |
| :--- | :--- |
| **[Executive Overview](overview.md)** | Problem statement, the "Shadow Surface Dilemma", OWASP API Top 10 vulnerabilities, and core value proposition. |
| **[System Architecture](architecture.md)** | End-to-end topology, Mermaid sequence diagrams, inline gateway lifecycle, and component breakdowns. |
| **[In-Flight Data Flow](architecture/data-flow.md)** | Detailed wire data flow through IP guards, route quarantine, async proxying, PII redaction, and WebSocket broadcast. |
| **[Telemetry Wire Schema](architecture/telemetry-schema.md)** | Standardized telemetry ingest wire-schema, payload formats, sensitive PII definitions, and gateway headers. |
| **[Feasibility & Compliance](feasibility.md)** | Sub-2ms latency benchmarking, Welford's $O(1)$ statistical profiling, economic ROI, and DPDP / RBI compliance analysis. |
| **[Threat Model & Security](security/threat-model.md)** | STRIDE security analysis, fail-open vs. fail-closed considerations, memory bounds, and audit disclosures. |
| **[Testing & Validation](testing/validation.md)** | Deep specification of all 130 tests, test commands, and reproducible 140-event benchmark simulation data. |
| **[Developer Setup & Troubleshooting](development/setup.md)** | Multi-service local setup instructions, virtual environment management, and port conflict resolution. |
| **[SOC Console Implementation](development/soc-console.md)** | Technical overview of the React 18 / Vite SOC frontend, state flow, and UI components. |
| **[Vite Template Notes](development/vite-template-notes.md)** | Modern React + Vite development setup, HMR configuration, and plugin guides. |
| **[Pitch Deck](pitch_deck.md)** | 10-slide technical and executive overview presentation deck for Perimeter. |
| **[Visual Assets & Media](assets.md)** | Inventory of dashboard screenshots, visual media, and demo presentation artifacts. |

### Domain Deep Dives & Threat Specifications
| Document | Description |
| :--- | :--- |
| **[Simulation & Defense Guide](simulation.md)** | Comprehensive 8-scenario red-team cyberattack simulation guide covering OWASP API Top 10, deep payload & SSRF inspection, supply-chain guard, interactive attacker drawer, and threat simulator. |
| **[Live Attack Demo Script](simulation/live-attack-demo-script.md)** | Step-by-step scripted red-team exploitation walkthrough covering Zombie KYC dumps, Shadow API backdoors, and BOLA. |
| **[Target Vulnerability Registry](simulation/vulnerabilities.md)** | Catalog and CVSS v3.1 dossiers of synthetic vulnerabilities in the BharatPay test environment. |
| **[Identity & Access Governance](identity_access.md)** | Enterprise RBAC hierarchy, 6 privileged roles, jurisdiction-enforced reporting, sanctioned business campaign multipliers, and reasoning chains. |
| **[Context-Aware Session Graphing](session_graphing.md)** | Stateful Directed Acyclic Graphs (DAGs) per session, skip-step business flow violation detection (OWASP API6:2023), and Shannon branching entropy reconnaissance detection. |
| **[REST API Reference](api_reference.md)** | Complete technical documentation of all Perimeter Control-Plane and Ingress Gateway endpoints, payloads, and WebSocket streams. |

---

## ⚡ Quickstart Navigation

### 1. Launch All Services

```bash
# 1. Start BharatPay Core Banking Backend (Port 8001)
cd frontend/bharatpay/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 2. Start Perimeter Security Gateway (Port 8000)
# (from repository root)
python -m uvicorn person1_api_discovery.app.main:app --host 0.0.0.0 --port 8000

# 3. Start Perimeter SOC Console (Port 3000)
cd frontend/dashboard
npm run dev

# 4. Start BharatPay Customer Portal (Port 5173)
cd frontend/bharatpay/frontend
npm run dev
```

### 2. Service Endpoints
* **Perimeter SOC Dashboard:** [http://localhost:3000](http://localhost:3000)
* **Perimeter Security Gateway & API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **BharatPay Banking Web Portal:** [http://localhost:5173](http://localhost:5173)
* **BharatPay Core API:** [http://localhost:8001/health](http://localhost:8001/health)

### 3. Run Live Demonstrations and Tests
```bash
# Run the complete before-and-after attack & active defense demonstration
python demo_before_after.py

# Run the 4-part automated defense assertion suite
python verify_perimeter_defense.py

# Run red-team telemetry simulation
python simulate_bharatpay_attack.py

# Run all 130 unit, integration, and simulation tests
python -m pytest
```
