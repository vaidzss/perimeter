# CC6-IC07 Layer 2: Core Discovery, Abuse Detection & Risk Engine

An asynchronous, non-blocking telemetry engine for real-time API discovery, shadow/zombie route detection, OWASP Top 10 threat prevention, context-aware session graphing, and explainable risk scoring.

---

## 🌟 Core Architecture & Capabilities

### 1. Box A: Discovery & Shadow Diff Engine
- **Dynamic URL Parameterizer**: Auto-generalizes paths (`/accounts/9841` $\to$ `/accounts/{id}`) with entity parameter extraction.
- **Regex + Verhoeff Dihedral Group $D_5$ PII Classifier**: High-fidelity Indian DPI/FinTech scanner for PAN, UPI VPA, Phone, Email, and **zero-false-positive** Aadhaar detection.
- **OpenAPI 3.0 Diff Comparator**: Categorizes routes in real time into `DOCUMENTED`, `SHADOW`, and `ZOMBIE (v1)`.

### 2. Box B: Runtime Behavior & Abuse Detector
- **Welford $(\mu, \sigma)$ Baseline Profiler**: Numerically stable single-pass running statistics per endpoint.
- **BOLA / IDOR Sequence Detector (OWASP API1:2023)**: 60s sliding window tracking identity-object entropy and sequential enumeration.
- **Data Scraping & Harvesting Detector (OWASP API4:2023)**: Flags rates $> (\mu + 3\sigma)$ req/min ($Z > 3.0$) and response byte volume spikes.
- **Token Misuse & Replay Detector (OWASP API2:2023)**: Tracks concurrent JWT `jti` usage across divergent IP addresses and User-Agents.

### 3. Context-Aware Session Graphing Engine (OWASP API6:2023)
- **Stateful Markov Graph**: Builds Directed Behavioral Graphs (DAGs) per session.
- **Workflow Sequence Validation**: Catches out-of-order execution and skip-step attacks (e.g. calling financial transfers without prior session context).
- **Random-Walk Entropy**: Flags high-entropy reconnaissance crawlers ($H > 0.92$).
- **SOC Graph Topology Export**: Exposes `{ "nodes": [...], "edges": [...] }` for interactive Cytoscape / D3 graph visualizations.

### 4. Box C: Explainable Risk Scoring Engine
- **Weighted Composite Score (0–100)**:
  - 35% Exposure (Public unauth vs auth strength) $\to$ `API2:2023`
  - 25% PII Data Sensitivity (PAN / Aadhaar) $\to$ `API3:2023`
  - 20% Spec Drift (Shadow / Zombie status) $\to$ `API9:2023`
  - 20% Active Anomaly & Graph Abuse $\to$ `API1`, `API4`, `API6`
- **Explainable Reason Vectors**:
  ```json
  [ "+35 Unauth", "+25 PII (PAN/AADHAAR)", "+20 Shadow" ] -> 80/100
  ```

---

## 🚀 Standalone Poisson Threat Simulator

Includes a built-in mathematical threat simulator using Poisson arrival intervals ($\Delta t \sim \text{Exp}(\lambda)$) to generate mixed benign and multi-vector attack traffic:

```bash
# Run in-memory simulation benchmark (150 events @ 25 req/sec)
python simulator.py --mode=direct --events=150 --rate=25

# Stream live HTTP events to the server
python simulator.py --mode=http --target-url=http://localhost:8000/api/telemetry --events=100
```

---

## 📊 Performance & Evaluation Benchmarks

```
======================================================================
Ran 19 tests in 0.101s (OK)

[SIMULATOR BENCHMARK]
• Ingestion Latency:        0.095 ms / request (SLA < 0.5 ms)
• Engine Throughput:        ~10,500 requests / second / core
• True Positive Rate (TPR): 94.44%
• False Positive Rate (FPR): 0.0%
======================================================================
```

---

## 🛠️ Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Run complete test suite (19 unit & integration tests)
python -m unittest discover tests

# Launch FastAPI REST & WebSocket streaming server
python server.py
```

### Endpoints
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Telemetry Ingestion**: `POST http://localhost:8000/api/telemetry`
- **Session Graph Export**: `GET http://localhost:8000/api/session-graph/{session_id}`
- **Discovered Inventory**: `GET http://localhost:8000/api/inventory`
- **SOC Alert Queue**: `GET http://localhost:8000/api/alerts`
- **Real-Time Confusion Matrix**: `GET http://localhost:8000/api/metrics/confusion-matrix`
- **Live Push WebSocket**: `ws://localhost:8000/ws/telemetry`
