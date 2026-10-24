# Contributing to Perimeter

Thank you for your interest in contributing to **Perimeter**! We welcome contributions from engineers, security researchers, and open-source contributors.

This document outlines our engineering standards, development workflows, testing expectations, and contribution processes.

---

## Code of Conduct

All contributors and maintainers are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect, professionalism, and constructive feedback.

---

## Getting Started

### Prerequisites

* **Python:** 3.12 or newer
* **Node.js:** 18 LTS or newer (v20+ recommended)
* **npm:** 9+ or newer
* **Git:** 2.30+

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vaidzss/perimeter.git
   cd perimeter
   ```

2. **Set up Python Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies:**
   ```bash
   # SOC Dashboard
   cd frontend/dashboard
   npm install
   cd ../..

   # BharatPay Neobank Portal
   cd frontend/bharatpay/frontend
   npm install
   cd ../../..
   ```

4. **Initialize Seed Data:**
   ```bash
   python frontend/bharatpay/seed/seed.py
   ```

5. **Verify the Test Suite:**
   ```bash
   python -m pytest
   ```
   All 130 tests across unit, integration, and simulation suites should pass.

---

## Branching Strategy

* Main development branch: `main`
* Feature branches: `feat/<short-description>`
* Bug fixes: `fix/<issue-or-bug-name>`
* Documentation updates: `docs/<topic>`
* Refactoring / Code hygiene: `refactor/<target>`
* Performance tuning: `perf/<component>`

Always branch from the latest `main` branch:
```bash
git checkout main
git pull origin main
git checkout -b feat/dynamic-route-indexer
```

---

## Commit Message Conventions

We strictly follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short description in imperative mood>

[optional body explaining context and rationale]

[optional footer referencing issue numbers]
```

### Allowed Types

* `feat`: A new user-facing or detection capability
* `fix`: A bug fix or false-positive elimination
* `docs`: Documentation additions or revisions
* `refactor`: Code reorganization with no functional changes
* `perf`: Performance optimizations or latency reductions
* `test`: Adding or correcting tests
* `chore`: Build tasks, dependency updates, configuration changes

### Examples

```text
feat(detection): implement sliding-window entropy threshold for IDOR
fix(gateway): resolve CORS header duplication on preflight OPTIONS
docs(architecture): clarify Welford algorithmic complexity and bounds
test(engine): add test coverage for Verhoeff checksum validation
```

---

## Pull Request Requirements

Before opening a Pull Request (PR):

1. **Run full automated test suite:**
   ```bash
   python -m pytest
   ```
   PRs with failing tests will not be merged.

2. **Verify frontend builds:**
   ```bash
   cd frontend/dashboard && npm run build && cd ../..
   cd frontend/bharatpay/frontend && npm run build && cd ../../..
   ```

3. **Check for regressions:**
   Verify that existing active defense assertions pass:
   ```bash
   python -m pytest tests/test_target_service.py
   ```

4. **Self-Review Checklist:**
   * No hardcoded personal or machine-specific file paths.
   * No plaintext secrets, tokens, or private credentials committed.
   * Synthetic test data used exclusively for all examples and tests.
   * Type hints provided for all new Python functions and methods.
   * Documentation updated if changes affect configuration or APIs.

---

## Security-Sensitive Changes

Changes touching the following modules require explicit security review:
* Ingress reverse proxy (`person1_api_discovery/app/gateway.py`)
* Active defense policies (`person1_api_discovery/app/routers/defense_router.py`)
* PII regex and Verhoeff validation (`traffic-detection-engine/core/discovery/pii_classifier.py`)
* JWT token parsing and validation (`person1_api_discovery/app/auth.py`)

If you discover a potential vulnerability in Perimeter itself, **do NOT open a public GitHub issue**. Please follow the process in [SECURITY.md](SECURITY.md).

---

## Bug Reports and Feature Proposals

* **Bug Reports:** Open an issue using our Bug Report template. Include clear steps to reproduce, actual vs. expected behavior, and environment details.
* **Feature Requests:** Open an issue using our Feature Request template. Clearly explain the problem space, use case, and architectural approach.
