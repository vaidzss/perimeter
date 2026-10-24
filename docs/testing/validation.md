# Perimeter Testing & Validation Specification

This document details the test suites, verification methodologies, and benchmark reproducibility standards for **Perimeter**.

---

## 1. Test Architecture Overview

Perimeter's test suite consists of **130 automated test cases** distributed across four primary functional domains:

```text
tests/ (130 Total Tests)
├── tests/test_target_service.py (7 tests)
│   └── Standalone mock banking service compliance and baseline spec checks
├── person1_api_discovery/tests/ (47 tests)
│   ├── test_checkpoint1.py (9 tests) - Gateway ingress & domain routes
│   ├── test_checkpoint2.py (4 tests) - Inventory generation & drift classification
│   ├── test_checkpoint3.py (3 tests) - Auto-Swagger OpenAPI synthesis
│   ├── test_checkpoint5.py (6 tests) - OWASP attack vectors & payload sampling
│   ├── test_deep_inspector.py (16 tests) - SSRF, ReDoS, and AST complexity
│   ├── test_person1_pipeline.py (1 test) - End-to-end gateway discovery pipeline
│   ├── test_phase2_blindspots.py (2 tests) - Advanced bypass evasion checks
│   └── test_supply_chain_guard.py (6 tests) - Third-party API contract guards
├── traffic-detection-engine/tests/ (20 tests)
│   ├── test_box_a.py (4 tests) - URL parameterizer & Verhoeff PII validation
│   ├── test_box_b.py (4 tests) - Welford algorithm, BOLA, scraping, replay
│   ├── test_box_c.py (3 tests) - Explainable risk scoring & reason vectors
│   ├── test_session_graph.py (3 tests) - Markov behavioral DAG & sequence checks
│   ├── test_server.py (5 tests) - Standalone telemetry ingestion REST endpoints
│   └── test_e2e_simulation.py (1 test) - 140-event confusion matrix benchmark
└── frontend/bharatpay/backend/tests/ (56 tests)
    ├── test_attacks.py (4 tests) - Targeted neobank attack reproduction
    ├── test_auth.py (7 tests) - Neobank JWT authentication & claims
    ├── test_banking.py (5 tests) - UPI payments, transfers, balance queries
    ├── test_checkpoint11.py (3 tests) - Privileged role norms & scopes
    ├── test_checkpoint12.py (5 tests) - Employee onboarding & access grants
    ├── test_checkpoint13.py (5 tests) - Scope enforcement & internal reports
    ├── test_checkpoint14.py (6 tests) - Campaign windows & stolen token alerts
    ├── test_checkpoint15.py (3 tests) - Prioritized alert triage metadata
    ├── test_checkpoint16.py (3 tests) - Live workflow assertions
    ├── test_logging.py (4 tests) - Structured JSONL audit logging
    ├── test_seed_realism.py (5 tests) - Synthetic dataset distribution
    ├── test_shadow_endpoints.py (4 tests) - Undocumented routes existence
    └── test_spec.py (2 tests) - Baseline OpenAPI spec compliance
```

---

## 2. Test Execution Commands

### Execute All 130 Tests in Unified Run
```bash
python -m pytest
```

### Run Specific Subsystems
```bash
# Ingress Gateway & Discovery Tests (47 tests)
python -m pytest person1_api_discovery/tests/

# Mathematical Threat Detection Tests (20 tests)
python -m pytest traffic-detection-engine/tests/

# Upstream Neobank Target Tests (56 tests)
python -m pytest frontend/bharatpay/backend/tests/

# Standalone Target Service Tests (7 tests)
python -m pytest tests/test_target_service.py
```

---

## 3. Benchmark Reproducibility

To evaluate the mathematical detection engine's confusion matrix and execution latency on the standardized 140-event dataset:

```bash
python -m pytest traffic-detection-engine/tests/test_e2e_simulation.py -s
```

### Controlled Dataset Composition (140 Events)
1. **50 Benign Requests:** Legitimate authenticated banking operations with valid JWTs, standard rates, and documented endpoints.
2. **20 BOLA Requests:** Sequential enumeration of distinct account IDs under a single authenticated identity.
3. **25 Scraping Requests:** High-velocity crawl of customer profiles exceeding baseline velocity limits.
4. **15 Token Replay Requests:** Identical `jti` tokens replayed simultaneously across disparate Tor exit nodes.
5. **15 Zombie API Requests:** Direct calls to deprecated v1 bulk export endpoints.
6. **15 Shadow API Requests:** Calls to uncataloged internal debug backdoors.

### Benchmark Criteria & Verified Results
* **Detection SLA:** Average latency per event $< 0.5\text{ ms}$ (Measured: **$0.193\text{ ms}$**).
* **True Positive Rate (TPR):** Target $\ge 90\%$ (Measured: **$94.44\%$**).
* **False Positive Rate (FPR):** Target $\le 5\%$ (Measured: **$0.0\%$**).
