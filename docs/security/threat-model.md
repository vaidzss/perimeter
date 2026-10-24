# Perimeter: Threat Model & Security Considerations

This document outlines the architectural threat model for the **Perimeter ASPM and Active Defense platform**, applying the **STRIDE** methodology and mapping against the **OWASP API Security Top 10 (2023)**.

---

## 1. System Scope & Boundaries

Perimeter operates as an inline reverse proxy positioned at the network ingress boundary. It intercepts client HTTP/HTTPS requests before forwarding them to upstream backend services.

```text
[External Clients / Attackers]
           │
═══════════╪═══════════════════════════════════════════════════════════════ Boundary 1: Untrusted Ingress
           ▼
[Perimeter Ingress Gateway (:8000)]
   ├─ IP Quarantine Filter
   ├─ Route Quarantine Filter
   ├─ PII In-Flight Masking
   └─ Telemetry Mirroring Engine
           │
═══════════╪═══════════════════════════════════════════════════════════════ Boundary 2: Internal Mesh
           ▼
[Upstream Application / Neobank (:8001)]
```

---

## 2. STRIDE Analysis of Perimeter

| Threat Category | Potential Attack Vector | Perimeter Defense / Mitigation |
| :--- | :--- | :--- |
| **Spoofing** | Attacker spoofs `X-Forwarded-For` header to bypass IP blacklisting. | Gateway resolves client IP from direct socket connection (`request.client.host`) as authoritative source unless configured with trusted proxy CIDR ranges. |
| **Tampering** | Attacker modifies telemetry events or attempts to poison Welford statistical baselines. | Welford updates are bounded and evaluated on parameter templates rather than attacker-controlled arbitrary paths. Bounded circular deques (`maxlen=2000`) limit impact of volume bursts. |
| **Repudiation** | Operator claims an enforcement event was not triggered. | Tamper-evident structured logs record every quarantine decision with timestamps, IP attribution, route template, and justification string. |
| **Information Disclosure** | Perimeter gateway logs leak customer PII (Aadhaar, PAN) into plain logfiles. | Middleware and gateway apply regex masking (`mask_sensitive_pii`) before writing logs to disk or emitting telemetry streams over WebSockets. |
| **Denial of Service** | High-velocity flood aimed at crashing the gateway or filling server memory. | Algorithmic operations are $O(1)$ complexity (hash lookups, Welford updates). Bounded memory circular buffers guarantee RAM consumption remains strictly capped. |
| **Elevation of Privilege** | Attacker attempts to call Perimeter control-plane endpoints (`/api/defense/quarantine`) to alter defense policies. | Defense management endpoints are segregated under dedicated `/api/defense/*` router and can be restricted to internal management interfaces or authorized admin tokens. |

---

## 3. Operational & Failure Modes

### Fail-Open vs. Fail-Closed
* **Default Gateway Behavior:** If the upstream target service is unreachable, the gateway returns `HTTP 502 Bad Gateway`.
* **Telemetry Decoupling:** Telemetry processing and mathematical scoring operate asynchronously and non-blockingly. If the detection engine encounters an internal exception, the ingress proxy continues forwarding traffic to ensure business continuity.
* **Process Interruption:** If the Perimeter gateway process itself terminates, network traffic cannot flow to upstream backends unless an external load balancer (AWS ALB, Nginx, or HAProxy) is configured with automated health check failover.

---

## 4. Audit & Compliance Disclosure

> [!WARNING]
> **Independent Audit Notice:** Perimeter is open-source security software in active development. **It has not yet undergone an independent third-party security audit or formal regulatory compliance certification (e.g., ISO 27001, SOC 2, or PCI-DSS).** Organizations evaluating Perimeter for production deployment should conduct internal architecture reviews, validate threat boundaries, and test high-availability failover configurations.
