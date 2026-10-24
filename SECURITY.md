# Security Policy

The Perimeter project takes the security of its API defense platform, microservice infrastructure, and users seriously.

---

## Supported Versions

Only the latest release on the primary development branch (`main`) is actively supported with security updates.

| Version / Branch | Supported          |
| :--------------- | :----------------- |
| `main` (2.x)     | :white_check_mark: |
| < 2.0.0          | :x:                |

---

## Reporting a Vulnerability

If you discover a security vulnerability or weakness within Perimeter, **please do NOT report it in public GitHub issues, discussions, or social channels**.

### Preferred Reporting Method

Please report security issues through **GitHub Private Vulnerability Reporting**:
1. Navigate to the repository's [Security Advisories](https://github.com/vaidzss/perimeter/security/advisories) page.
2. Click **"Report a vulnerability"** to submit a private report directly to the repository maintainers.

If GitHub Private Vulnerability Reporting is not accessible, you may reach out privately to the maintainers through the verified profile contact on GitHub (`@vaidzss`).

### What to Include in Your Report

To help us investigate and remediate the issue effectively, please include:
* A detailed description of the vulnerability and its potential impact.
* Step-by-step instructions or a minimal Proof of Concept (PoC) script.
* Affected components (e.g. gateway proxy, scoring engine, dashboard adapter).
* Any suggested fixes or mitigations if identified.

### Responsible Disclosure Guidelines

* **Do not include real customer or personal identifiable information (PII).** Always use synthetic test identifiers.
* **Do not include live production credentials**, API keys, or private keys.
* Allow maintainers reasonable time to investigate, reproduce, and patch the issue before any public disclosure.

---

## Security Practices in Perimeter

* **Synthetic Data Standard:** All demonstration scripts, seed data, and tests utilize purely synthetic test identifiers (`Priya Sharma`, `[GOVT-ID-XXXX-XXXX]`, `ABCDE1234F`). No genuine citizen or banking data is stored or processed.
* **Environment Hygiene:** Credentials and signing keys are passed strictly through environment variables or `.env` files. Safe defaults are provided only for local non-production testing.
* **Non-Blocking Telemetry:** Traffic inspection and scoring operate non-blockingly to maintain resilience and minimize operational risk for upstream services.
