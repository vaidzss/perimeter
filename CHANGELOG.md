# Changelog

All notable changes to the **Perimeter** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Root `pytest.ini` with unified test configuration across gateway, detection engine, and target neobank suites (`130 passed`).
- Comprehensive root `.env.example`, `.editorconfig`, `.gitattributes`, and `LICENSE` (Apache 2.0).
- Standardized open-source repository governance: `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md`.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) executing Python test suites, TypeScript type checks, and Vite production builds.
- GitHub issue templates (`bug_report.md`, `feature_request.md`) and pull request template (`pull_request_template.md`).
- Consolidated documentation hub in `docs/` with cross-platform commands and verified relative links.

### Changed
- Replaced machine-specific hardcoded paths with portable `$PSScriptRoot` and relative repository paths in `run_all.ps1` and documentation.
- Renamed test module `tests/test_checkpoint1.py` to `tests/test_target_service.py` to eliminate test collection collisions.
- Reorganized loose documentation imagery into `docs/images/`.
- Qualified performance and benchmark claims to accurately distinguish synthetic simulation benchmarks from production guarantees.

---

## [2.1.0] - 2026-10-16

### Added
- Comprehensive 8-scenario red-team cyberattack simulation covering OWASP API Security Top 10 (2023).
- Deep semantic inspection suite and supply-chain defense guard (`SafeExternalAPIClient`).
- In-flight Aadhaar and PAN redaction using UIDAI-compliant Verhoeff dihedral group $D_5$ checksum and regex matching.
- Real-time Directed Behavioral Graph (DAG) construction with session entropy tracking.
- Interactive SOC Command Center Console featuring live Security Posture Scores, dynamic inventory drift analysis, and allowed-vs-blocked resolution tracking.

### Fixed
- Tuned threat evaluation threshold and expanded session graph anchors to eliminate false positives in legitimate customer banking journeys.

---

## [2.0.0] - 2026-10-15

### Added
- Core integration of Perimeter Ingress Security Gateway (`person1_api_discovery`), Traffic Detection Engine (`traffic-detection-engine`), and BharatPay Neobank target application (`frontend/bharatpay`).
- Box A: Dynamic URL parameterizer, PII classifier, and OpenAPI 3.0 spec reconciler.
- Box B: Welford's algorithm for $O(1)$ numerically stable online mean and variance profiling, BOLA detector, credential replay detector, and scraping detector.
- Box C: Explainable composite risk scoring (0-100) with reason vectors.
- Active defense quarantine filters for routes and malicious IP addresses.
