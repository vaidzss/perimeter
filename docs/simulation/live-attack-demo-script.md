# 5-MINUTE LIVE-ATTACK DEMO SCRIPT
## Perimeter API Defense Live Demonstration Guide

**Presenter:** Alex Vance (Lead Presenter)  
**Co-Presenter / Demo Operator:** Live Console Pilot  
**Target Duration:** Exactly 5 Minutes (00:00 to 05:00)  
**Prerequisites:** 
- Backend REST Server running on `http://localhost:5000`
- React SOC Dashboard open on `http://localhost:3000`
- Terminal window open with curl commands ready (optional backup)

---

### Timeline Overview
* **00:00 - 01:00:** Minute 1 — The Hook & The Posture Blindspot
* **01:00 - 02:00:** Minute 2 — Shadow API Discovery & Schema Drift
* **02:00 - 03:00:** Minute 3 — The Live Attack (Executing BOLA Exploit)
* **03:00 - 04:00:** Minute 4 — Forensic Deep Dive in the Investigation Workbench
* **04:00 - 05:00:** Minute 5 — Autonomous Mitigation & The WOW Finish

---

### MINUTE 00:00 - 01:00: The Hook & The Posture Blindspot

#### Screen / View:
Open on **Security Posture (Overview)** tab (`http://localhost:3000`).

#### Presenter Spoken Script:
> *"Judges, over 80% of enterprise internet traffic today is API traffic. Every modern fintech and cloud app is powered by microservices. But here is the dirty secret in cybersecurity: traditional WAFs like Cloudflare or AWS WAF are completely blind to modern API attacks.*  
> 
> *A WAF looks for SQL injections or cross-site scripting strings. When an attacker abuses business logic to steal data, the WAF sees a valid TLS handshake, a valid bearer token, and a 200 OK response. It lets the exfiltration happen right through.*  
> 
> *Welcome to Sentinel Defense. Here in our SOC console, we monitor our production banking cluster across 142 microservices. Notice our Security Posture Score is 68 out of 100—Grade B-. Our passive eBPF sensor has already flagged 18 uncataloged Shadow APIs and 12 Broken Object Level Authorization vulnerabilities."*

#### Actions on Screen:
1. Hover over the **Security Posture Gauge** (68 / 100).
2. Point out the **OWASP API Security Top 10** chart showing `API1:2023 - BOLA` as the highest count.
3. Click on the **18 Shadow APIs** pill in the KPI cards to transition seamlessly into the inventory.

---

### MINUTE 01:00 - 02:00: Continuous Discovery & The Shadow API

#### Screen / View:
Open on **API Inventory** tab.

#### Presenter Spoken Script:
> *"Let's take a look at our live API Inventory. Unlike static catalogs that require developers to manually update Swagger files, Sentinel continuously sniffs live traffic to discover endpoints.*  
> 
> *Look at line two: `/internal/v1/debug/tokens`. It is tagged with `#Shadow-API` in flashing purple. An engineer deployed this internal route to debug a session issue last week, but forgot to configure an authentication guard or add it to the gateway router. Anyone can query this endpoint from the public internet and dump active cluster admin tokens.*  
> 
> *Now look at line one: `/api/v2/users/{id}/financial-profile`. It is marked with `Drift`. Let's click into its risk breakdown."*

#### Actions on Screen:
1. Filter the inventory table by typing `debug` or clicking `Status: Shadow`.
2. Click on `/api/v2/users/{id}/financial-profile` to open the **API Detail Modal**.
3. Highlight:
   * Composite Risk Score: **94/100 (Critical)**
   * Granular Risk Factors: **Broken Object Level Authorization (BOLA)** and **Cleartext SSN Exposure**.
   * Switch to the **Parameters & Drift** tab: Show the undocumented query param `?include_raw_records=true` discovered in production traffic.
4. Close modal and get ready for the attack.

---

### MINUTE 02:00 - 03:00: The Live Attack (Executing BOLA Exploit)

#### Screen / View:
Return to main console or stay on Threat Alerts view.

#### Presenter Spoken Script:
> *"Now let's put ourselves in the shoes of an attacker. Our attacker is operating from IP `194.26.29.112` through a Dutch Tor exit node.*  
> 
> *The attacker creates a legitimate, low-privilege test account (`test_user_42`) and obtains a genuine, valid JWT token. Next, instead of viewing their own account, they manipulate the user UUID in the URL path to iterate through foreign customer accounts: `usr_84920480`, `usr_84920481`, `usr_84920482`.*  
> 
> *Let's trigger this live burst right now!"*

#### Actions on Screen:
1. Click the top navbar button: **"Simulate Live BOLA Attack"** (or run the terminal curl command below).
2. Point out the live alert banner popping up in red: **"CRITICAL: BOLA Exfiltration Burst Detected!"**
3. Notice the active alerts counter increments from 4 to 5.

#### Terminal Command (Backup / Live Execution):
```bash
curl -X POST "http://localhost:5000/api/v1/simulate-attack" \
  -H "Content-Type: application/json" \
  -d '{"type": "bola"}'
```

---

### MINUTE 03:00 - 04:00: Deep Forensic Investigation Drill-Down

#### Screen / View:
Click **"Drill Into Investigation"** button on alert `#alt-9821` to load the **Investigation View**.

#### Presenter Spoken Script:
> *"Within 40 milliseconds, Sentinel's behavioral engine classified the anomaly and raised Alert #alt-9821. Let's drill into the incident.*  
> 
> *Look at our Investigation Workbench. On the left, we have the complete Attacker Intelligence Profile: Source IP 194.26.29.112, Reputation Score 98 (Malicious Bot), JA3 and JA4 TLS fingerprints, and headless Python user-agent.*  
> 
> *In the center, look at our 5-stage Chronological Incident Reconstruction:*  
> * Stage 1: Reconnaissance — Attacker authenticated with disposable email.  
> * Stage 2: Vulnerability Probe — Attacker probed the shadow `/internal/v1/debug/tokens` endpoint.  
> * Stage 3: Exploitation — Attacker executed first parameter ID tamper.  
> * Stage 4: High-Rate Exfiltration — 142 requests in 25 seconds stealing 42 VIP customer records.  
> 
> *Now, look at the Raw HTTP Inspector below. Let's compare the headers and response. The caller's JWT subject is `usr_10001`, but the URL requested is `usr_84920482`. Look at the response payload: cleartext SSN `482-90-1193` and bank balance `$142,850.45` were leaked! We can even click 'Copy as cURL' to replay the packet in terminal.*  
> 
> *Finally, look at the Actor's Global Blast Radius table: Sentinel automatically correlates every single microservice this actor touched across their entire session."*

#### Actions on Screen:
1. Scroll down through the **Chronological Incident Timeline**.
2. Click **Sample #1** and **Sample #2** in the Raw HTTP Request/Response viewer.
3. Click **"Copy as cURL"** (shows green checkmark).
4. Point to the **Actor's Global Blast Radius & Lateral Activity** table showing all 4 targeted microservices.

---

### MINUTE 04:00 - 05:00: Autonomous Mitigation & The WOW Finish

#### Screen / View:
Stay on **Investigation View** top action bar, then navigate to **Traffic Analytics**.

#### Presenter Spoken Script:
> *"In a typical enterprise, remediating this requires opening a JIRA ticket, waiting for the engineering sprint, refactoring the authorization middleware, and redeploying the service—a 2-to-3 week window of ongoing exposure.*  
> 
> *With Sentinel, we mitigate this in two clicks, in less than two seconds.*  
> 
> *First, I click 'Block Actor IP'. Sentinel immediately pushes an edge drop rule across all Envoy instances in 12 milliseconds.*  
> 
> *Second, we apply our Zero-Downtime Virtual Patch. The virtual patch automatically enforces response masking at egress—redacting SSNs to XXX-XX-last4 and verifying user ownership headers—with zero downtime and zero code changes.*  
> 
> *Let's verify our Traffic Analytics. Look at the real-time throughput chart: clean traffic continues uninterrupted at 380 requests/second, while all malicious probe requests are dropped with HTTP 403 Forbidden.*  
> 
> *Judges, Sentinel turns every API into a self-defending, continuously governed asset. Thank you, and we'd love to take your questions!"*

#### Actions on Screen:
1. Click **"Block Actor IP (194.26.29.112)"** in the top action bar. Notice the badge turns to green: **"Actor Blocked Globally"**.
2. Click **"Mark Mitigated"**.
3. Switch to the **Traffic Analytics** tab:
   * Show the stacked throughput chart (Clean RPS in cyan vs Malicious drop spikes in red).
   * Show the HTTP 403 Forbidden blocked ratio.
   * Point out the Top Actors table showing `194.26.29.112` marked as `BLOCKED`.
4. Finish on schedule at **04:55** for judge applause.

---

### Speaker Cue Card Cheat Sheet (Printable)
| Time | View | Key Line to Deliver | Key Click |
|---|---|---|---|
| **0:30** | Overview | *"WAFs see valid 200 OKs; they are blind to BOLA."* | Hover over Posture Score (68) |
| **1:15** | Inventory | *"Notice /internal/v1/debug/tokens—a live shadow API."* | Filter by `status: shadow` |
| **2:10** | Any | *"Attacker logs in, gets JWT, but tampers with UUIDs."* | Click **Simulate Live BOLA Attack** |
| **3:10** | Investigation | *"Look at the timeline: from reconnaissance to exfiltration."* | Click **Drill Into Investigation** |
| **3:40** | Raw HTTP | *"JWT is usr_10001, but payload returns victim's cleartext SSN."* | Toggle Request Samples 1 & 2 |
| **4:20** | Action Bar | *"Mitigation in 2 clicks: Block Actor IP and Virtual Patch."* | Click **Block Actor IP** & **Mitigate** |
| **4:50** | Traffic | *"Clean traffic flows; exploit is dropped at edge. 403 Forbidden."* | Show Traffic Analytics |

---
**End of Demo Script.**
