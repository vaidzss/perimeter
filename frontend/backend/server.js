const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// In-Memory Database State initialized from realistic schemas
let overviewPosture = {
  overallScore: 68,
  grade: 'B-',
  riskSummary: { critical: 4, high: 9, medium: 14, low: 22 },
  postureBreakdown: [
    {
      category: 'Object-Level Authorization (BOLA/BOPLA)',
      score: 48,
      status: 'critical',
      issuesCount: 12,
      description: 'Critical object ID manipulation detected across 4 financial microservices',
    },
    {
      category: 'Shadow & Unmanaged APIs',
      score: 55,
      status: 'critical',
      issuesCount: 8,
      description: '8 uncataloged routes discovered bypassing API gateway & security controls',
    },
    {
      category: 'Authentication & Credential Posture',
      score: 62,
      status: 'warning',
      issuesCount: 7,
      description: 'Weak JWT signature verification and unexpired debug token exposure',
    },
    {
      category: 'Sensitive Data Exposure & PII Leakage',
      score: 74,
      status: 'warning',
      issuesCount: 5,
      description: 'Cleartext SSN, credit card masks, and tax IDs found in 5 response schemas',
    },
    {
      category: 'Rate Limiting & Anti-Abuse Controls',
      score: 85,
      status: 'good',
      issuesCount: 2,
      description: 'Most public endpoints protected by token bucket rate limiters',
    },
  ],
  kpis: {
    totalApis: 142,
    shadowApis: 18,
    zombieApis: 7,
    criticalAlerts: 4,
    sensitiveDataExposures: 26,
    blockedAttacks24h: 1845,
    trafficRps: 342,
    dataLossPreventionSaves: 340,
  },
  owaspTop10Distribution: [
    { code: 'API1:2023', name: 'Broken Object Level Authorization (BOLA)', shortName: 'BOLA / IDOR', count: 14, severity: 'critical' },
    { code: 'API2:2023', name: 'Broken Authentication', shortName: 'Broken Auth', count: 9, severity: 'high' },
    { code: 'API3:2023', name: 'Broken Object Property Level Auth', shortName: 'BOPLA / Mass Assign', count: 8, severity: 'high' },
    { code: 'API4:2023', name: 'Unrestricted Resource Consumption', shortName: 'Rate Limit Bypass', count: 12, severity: 'medium' },
    { code: 'API5:2023', name: 'Broken Function Level Auth', shortName: 'BFLA / Privilege Esc.', count: 5, severity: 'high' },
    { code: 'API6:2023', name: 'Unrestricted Access to Sensitive Flows', shortName: 'Business Flow Abuse', count: 7, severity: 'medium' },
    { code: 'API7:2023', name: 'Server Side Request Forgery (SSRF)', shortName: 'SSRF', count: 3, severity: 'critical' },
    { code: 'API8:2023', name: 'Security Misconfiguration', shortName: 'Misconfiguration', count: 11, severity: 'medium' },
    { code: 'API9:2023', name: 'Improper Inventory Management', shortName: 'Shadow / Zombie APIs', count: 18, severity: 'high' },
    { code: 'API10:2023', name: 'Unsafe Consumption of Third-Party APIs', shortName: 'Unsafe 3rd Party APIs', count: 4, severity: 'low' },
  ],
  riskTrend: [
    { date: '10/07', critical: 6, high: 11, medium: 16, low: 25, postureScore: 61 },
    { date: '10/08', critical: 7, high: 12, medium: 15, low: 24, postureScore: 59 },
    { date: '10/09', critical: 5, high: 10, medium: 15, low: 24, postureScore: 65 },
    { date: '10/10', critical: 5, high: 10, medium: 14, low: 23, postureScore: 66 },
    { date: '10/11', critical: 4, high: 9, medium: 15, low: 22, postureScore: 68 },
    { date: '10/12', critical: 4, high: 9, medium: 14, low: 22, postureScore: 68 },
    { date: '10/13', critical: 4, high: 9, medium: 14, low: 22, postureScore: 68 },
  ],
  threatGeos: [
    { country: 'Netherlands (Tor Exit / Hosting)', code: 'NL', attacks: 612, percentage: 33.2 },
    { country: 'Russia (Bulletproof ASN 49304)', code: 'RU', attacks: 485, percentage: 26.3 },
    { country: 'United States (Compromised AWS/DO)', code: 'US', attacks: 340, percentage: 18.4 },
    { country: 'Seychelles (Anonymous Proxy)', code: 'SC', attacks: 230, percentage: 12.5 },
    { country: 'Germany (Scraping Cloud)', code: 'DE', attacks: 178, percentage: 9.6 },
  ],
};

let inventory = [
  {
    id: 'api-001',
    method: 'GET',
    path: '/api/v2/users/{id}/financial-profile',
    service: 'customer-banking-service',
    host: 'api.cybercup.corp',
    environment: 'production',
    status: 'managed',
    riskScore: 94,
    riskLevel: 'critical',
    authType: 'JWT Bearer',
    piiDetected: ['SSN', 'Bank Account No', 'Credit Score', 'Annual Income'],
    rps: 42.5,
    lastSeen: '2026-10-13T22:24:18Z',
    specDrift: true,
    tags: ['Financial', 'BOLA-Vulnerable', 'High-PII', 'Core-Banking'],
    activeThreatCount: 2,
    riskBreakdown: {
      factors: [
        {
          name: 'Broken Object Level Authorization (BOLA / IDOR)',
          score: 95,
          impact: 'Caller tenant or user ID is NOT validated against the path parameter {id}. Any valid session token can iterate user IDs and dump foreign accounts.',
          owasp: 'API1:2023 - Broken Object Level Authorization',
          mitigated: false,
        },
        {
          name: 'Sensitive PII / Financial Data Exposure',
          score: 89,
          impact: 'Response payload serializes cleartext SSN, credit score rating, and bank routing numbers without field-level masking.',
          owasp: 'API3:2023 - Broken Object Property Level Auth',
          mitigated: false,
        },
        {
          name: 'OpenAPI Specification Drift',
          score: 72,
          impact: 'Endpoint accepts undocumented query parameter ?include_raw_records=true which bypasses pagination and outputs full credit ledger.',
          owasp: 'API9:2023 - Improper Inventory Management',
          mitigated: false,
        },
        {
          name: 'Insufficient Request Throttling',
          score: 55,
          impact: 'Allows up to 500 requests/minute per IP before HTTP 429 trigger, enabling automated enumeration.',
          owasp: 'API4:2023 - Unrestricted Resource Consumption',
          mitigated: true,
        },
      ],
      remediationGuidance: [
        'Enforce Resource-Level ABAC/RBAC: Validate that req.user.tenantId matches the owner of target user {id} in the repository layer.',
        'Deploy Response Masking Virtual Patch: Redact field "ssn" to "XXX-XX-" + last4, and mask bank account numbers before serialization.',
        'Regenerate OpenAPI v3.1 Spec: Remove undocumented parameter "include_raw_records" from production builds.',
        'Tighten Rate Limiter: Set bursting threshold to 15 req/min for financial profile endpoints.',
      ],
    },
    parameters: [
      { name: 'id', in: 'path', type: 'string (UUID)', required: true, sensitive: false, description: 'Unique target customer identifier' },
      { name: 'include_raw_records', in: 'query', type: 'boolean', required: false, sensitive: true, description: 'Undocumented debug flag dumping internal ledger' },
      { name: 'Authorization', in: 'header', type: 'string', required: true, sensitive: true, description: 'Standard Bearer JWT session token' },
      { name: 'X-Client-Version', in: 'header', type: 'string', required: false, sensitive: false, description: 'Mobile client build version' },
    ],
    samplePayloads: {
      request: {
        method: 'GET',
        url: 'https://api.cybercup.corp/api/v2/users/usr_84920482/financial-profile?include_raw_records=true',
        headers: {
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-z3...',
          'User-Agent': 'python-requests/2.31.0',
          'X-Client-Version': 'v2.4.1',
        },
      },
      response: {
        status: 200,
        body: {
          account_id: 'usr_84920482',
          full_name: 'Alexander M. Wright',
          ssn: '482-90-1193',
          credit_score: 792,
          routing_number: '121000358',
          account_balance: 142850.45,
          active_loans: [{ loan_id: 'ln-9912', amount: 35000.00, status: 'current' }],
          internal_risk_rating: 'VIP_PLATINUM_TIER',
        },
      },
    },
    schemaDrift: {
      hasDrift: true,
      undocumentedFields: ['include_raw_records', 'internal_risk_rating', 'routing_number'],
      missingRequiredFields: ['X-Request-Correlation-ID'],
      lastSpecSync: '2026-09-18T14:22:00Z',
    },
    mitigationStatus: {
      quarantined: false,
      virtualPatched: false,
      wafRuleActive: true,
    },
  },
  {
    id: 'api-002',
    method: 'GET',
    path: '/internal/v1/debug/tokens',
    service: 'auth-gateway-internal',
    host: 'gateway-int.cybercup.corp',
    environment: 'production',
    status: 'shadow',
    riskScore: 98,
    riskLevel: 'critical',
    authType: 'None (Public)',
    piiDetected: ['Master JWT Key', 'Admin Session Tokens', 'Internal IP'],
    rps: 8.2,
    lastSeen: '2026-10-13T22:25:01Z',
    specDrift: true,
    tags: ['Shadow-API', 'Admin-Leak', 'No-Auth', 'Urgent-Fix'],
    activeThreatCount: 1,
    riskBreakdown: {
      factors: [
        {
          name: 'Unauthenticated Shadow Debug Endpoint',
          score: 99,
          impact: 'Completely uncataloged internal route left exposed to the public Internet without any API Gateway auth guard.',
          owasp: 'API9:2023 - Improper Inventory Management',
          mitigated: false,
        },
        {
          name: 'Hardcoded Master Secrets Dump',
          score: 98,
          impact: 'Returns active cluster admin session tokens and signing secrets in response payload.',
          owasp: 'API2:2023 - Broken Authentication',
          mitigated: false,
        },
      ],
      remediationGuidance: [
        'Immediate Quarantine: Invalidate public ingress routing to /internal/* paths at Envoy / Cloudflare layer.',
        'Revoke Compromised Secrets: Rotate all master JWT signing keys generated before 2026-10-13.',
        'Run Shadow API Quarantine Workflow.',
      ],
    },
    parameters: [
      { name: 'scope', in: 'query', type: 'string', required: false, sensitive: false, description: 'Optional token scope filter' },
    ],
    samplePayloads: {
      request: {
        method: 'GET',
        url: 'https://gateway-int.cybercup.corp/internal/v1/debug/tokens',
        headers: { 'Host': 'gateway-int.cybercup.corp' },
      },
      response: {
        status: 200,
        body: {
          cluster: 'prod-us-east-1',
          active_admin_tokens: ['eyJhbGciOi...master_admin_token'],
          session_ttl: 86400,
          debug_mode: true,
        },
      },
    },
    schemaDrift: {
      hasDrift: true,
      undocumentedFields: ['Entire Endpoint Unregistered in OpenAPI Repository'],
      missingRequiredFields: [],
      lastSpecSync: 'Never Documented',
    },
    mitigationStatus: {
      quarantined: false,
      virtualPatched: false,
      wafRuleActive: false,
    },
  },
  {
    id: 'api-003',
    method: 'POST',
    path: '/api/v1/transfers/wire',
    service: 'payment-processing-engine',
    host: 'pay.cybercup.corp',
    environment: 'production',
    status: 'managed',
    riskScore: 88,
    riskLevel: 'critical',
    authType: 'mTLS + OAuth 2.0',
    piiDetected: ['IBAN', 'Recipient Name', 'Routing Number'],
    rps: 19.4,
    lastSeen: '2026-10-13T22:26:40Z',
    specDrift: false,
    tags: ['Payment', 'High-Risk', 'Wire-Transfer'],
    activeThreatCount: 1,
    riskBreakdown: {
      factors: [
        { name: 'Financial Transaction High Value Impact', score: 90, impact: 'Executes irreversible wire transfers between bank accounts', owasp: 'API6:2023', mitigated: true },
      ],
      remediationGuidance: ['Enforce step-up MFA and dynamic biometric signature verification on transfers > $5,000'],
    },
    parameters: [],
    samplePayloads: { request: {}, response: {} },
    schemaDrift: { hasDrift: false, undocumentedFields: [], missingRequiredFields: [], lastSpecSync: '2026-10-10' },
    mitigationStatus: { quarantined: false, virtualPatched: false, wafRuleActive: true },
  },
  {
    id: 'api-004',
    method: 'PUT',
    path: '/api/v1/users/{id}/profile',
    service: 'user-management-service',
    host: 'api.cybercup.corp',
    environment: 'production',
    status: 'managed',
    riskScore: 78,
    riskLevel: 'high',
    authType: 'JWT Bearer',
    piiDetected: ['Email', 'Phone', 'Role Flag', 'IsAdmin'],
    rps: 65.1,
    lastSeen: '2026-10-13T22:26:10Z',
    specDrift: true,
    tags: ['BOPLA-Risk', 'Mass-Assignment', 'User-Data'],
    activeThreatCount: 1,
    riskBreakdown: {
      factors: [
        { name: 'Mass Assignment Vulnerability', score: 85, impact: 'Accepts internal user flags like isAdmin without payload schema filter', owasp: 'API3:2023', mitigated: false },
      ],
      remediationGuidance: ['Implement DTO whitelist validation in controller'],
    },
    parameters: [],
    samplePayloads: { request: {}, response: {} },
    schemaDrift: { hasDrift: true, undocumentedFields: ['role', 'is_verified'], missingRequiredFields: [], lastSpecSync: '2026-09-01' },
    mitigationStatus: { quarantined: false, virtualPatched: false, wafRuleActive: false },
  },
  {
    id: 'api-006',
    method: 'GET',
    path: '/v1/legacy/export/customers.csv',
    service: 'crm-bridge-daemon',
    host: 'legacy.cybercup.corp',
    environment: 'production',
    status: 'zombie',
    riskScore: 91,
    riskLevel: 'critical',
    authType: 'Basic Auth (Weak)',
    piiDetected: ['Full Name', 'SSN', 'Address', 'Credit Card Last 4'],
    rps: 3.1,
    lastSeen: '2026-10-13T22:15:30Z',
    specDrift: true,
    tags: ['Zombie-API', 'Deprecated', 'Mass-Exfiltration', 'Unmanaged'],
    activeThreatCount: 1,
    riskBreakdown: {
      factors: [
        { name: 'Zombie API Deprecation Omission', score: 95, impact: 'Legacy CRM endpoint active 18 months after scheduled deprecation date', owasp: 'API9:2023', mitigated: true },
      ],
      remediationGuidance: ['Decommission virtual host and route traffic to HTTP 410 Gone'],
    },
    parameters: [],
    samplePayloads: { request: {}, response: {} },
    schemaDrift: { hasDrift: true, undocumentedFields: ['export_all'], missingRequiredFields: [], lastSpecSync: '2024-03-12' },
    mitigationStatus: { quarantined: true, virtualPatched: true, wafRuleActive: true },
  },
  {
    id: 'api-007',
    method: 'POST',
    path: '/api/v1/auth/login',
    service: 'identity-service',
    host: 'auth.cybercup.corp',
    environment: 'production',
    status: 'managed',
    riskScore: 72,
    riskLevel: 'high',
    authType: 'None (Public Entrypoint)',
    piiDetected: ['User Email', 'Hashed Password', 'Device Fingerprint'],
    rps: 154.2,
    lastSeen: '2026-10-13T22:27:00Z',
    specDrift: false,
    tags: ['Authentication', 'Credential-Stuffing-Target', 'Brute-Force'],
    activeThreatCount: 1,
    riskBreakdown: {
      factors: [
        { name: 'Credential Stuffing Vulnerability', score: 78, impact: 'Targeted by high-volume automated botnets using revolving proxies', owasp: 'API2:2023', mitigated: false },
      ],
      remediationGuidance: ['Enable invisible CAPTCHA and IP reputation screening at gateway'],
    },
    parameters: [],
    samplePayloads: { request: {}, response: {} },
    schemaDrift: { hasDrift: false, undocumentedFields: [], missingRequiredFields: [], lastSpecSync: '2026-10-01' },
    mitigationStatus: { quarantined: false, virtualPatched: false, wafRuleActive: true },
  },
];

let alerts = [
  {
    id: 'alt-identity-01',
    alert_id: 'alt-identity-01',
    title: 'Privileged Access: 2,000 Accounts Inspected by VP Sales during Diwali Sale 2026',
    severity: 'informational',
    category: 'Sanctioned Privileged Campaign',
    status: 'active',
    timestamp: '2026-10-15T10:30:00Z',
    targetEndpoint: '/api/v2/internal/reports/regional-sales',
    targetMethod: 'GET',
    actorIp: '103.21.244.1',
    actorCountry: 'India (Corporate Ingress)',
    actorFingerprint: 'JA3: e24a899014238b1b',
    owaspCategory: 'API1:2023 - Broken Object Level Authorization (Suppressed/Downgraded)',
    requestCount: 2000,
    blastRadius: '2,000 Regional Customer Records (Sanctioned Campaign)',
    isDowngraded: true,
    priorityTag: 'downgraded: sanctioned campaign activity',
    reasoningChain: [
      'role=VP, scope=org-wide, campaign=Diwali Sale 2026 active, volume within 5000/day limit -> informational',
      'Provisioned VP, in-scope, active campaign — downgraded from High to Informational'
    ],
    identityContext: {
      employeeId: 'EMP-1002',
      name: 'Sunita Rao',
      role: 'VP Sales',
      department: 'Sales',
      declaredScope: 'org-wide',
      activeCampaign: 'Diwali Sale 2026',
      baselineLimit: 200,
      campaignMultiplier: 10,
      effectiveLimit: 5000,
      volumeUsed: 2000
    },
    summary: 'Provisioned VP Sunita Rao accessed 2,000 accounts during active Diwali Sale 2026 campaign. Activity falls completely within declared org-wide scope and authorized 5,000/day multiplier limit. Downgraded from High to Informational.',
    assignedTo: 'Compliance Audit Lead'
  },
  {
    id: 'alt-identity-02',
    alert_id: 'alt-identity-02',
    title: 'Stolen Privileged Token / Geo-Anomaly on VP Sales (EMP-1002)',
    severity: 'critical',
    category: 'Stolen Privileged Identity',
    status: 'active',
    timestamp: '2026-10-15T11:15:22Z',
    targetEndpoint: '/api/v2/internal/reports/regional-sales',
    targetMethod: 'GET',
    actorIp: '185.220.101.5',
    actorCountry: 'Netherlands (Tor Exit Relay)',
    actorFingerprint: 'JA3: 771,4865-4866-4867,0-23-65281-10-11',
    owaspCategory: 'API2:2023 - Broken Authentication',
    requestCount: 150,
    blastRadius: 'VP Corporate Session Compromise',
    elevatedPriority: true,
    priorityTag: 'elevated priority: privileged identity + anomalous context',
    reasoningChain: [
      'Token claims VP Sales (EMP-1002) but request originates from Tor Exit Node 185.220.101.5 (Netherlands) with no prior session overlap.',
      'elevated priority: privileged identity + anomalous context'
    ],
    identityContext: {
      employeeId: 'EMP-1002',
      name: 'Sunita Rao',
      role: 'VP Sales',
      declaredScope: 'org-wide',
      anomaly: 'Untrusted origin: 185.220.101.5 (Netherlands Tor Exit)'
    },
    summary: 'Stolen VP Sales session token replayed from Netherlands Tor Exit node. High-privilege identity observed under anomalous foreign context. Priority elevated to Critical for immediate active defense containment.',
    assignedTo: 'SecOps Incident Response'
  },
  {
    id: 'alt-identity-03',
    alert_id: 'alt-identity-03',
    title: 'Cross-Jurisdiction Scope Violation: Sales Manager (West) accessed East accounts',
    severity: 'high',
    category: 'Privileged Scope Violation',
    status: 'active',
    timestamp: '2026-10-15T11:45:00Z',
    targetEndpoint: '/api/v2/internal/reports/account-lookup/{account_id}',
    targetMethod: 'GET',
    actorIp: '103.45.120.10',
    actorCountry: 'India (Corporate West Branch)',
    actorFingerprint: 'JA3: f112bb456980',
    owaspCategory: 'API1:2023 - Broken Object Level Authorization',
    requestCount: 5,
    blastRadius: '5 Out-of-Scope East Accounts Queried',
    elevatedPriority: true,
    priorityTag: 'elevated priority: privileged identity + anomalous context',
    reasoningChain: [
      'role=Sales Manager, declared_scope=region:West, accessed accounts in region:East -> scope violation.',
      'Accessing even one account outside declared scope raises an immediate alert, regardless of seniority.',
      'elevated priority: privileged identity + anomalous context'
    ],
    identityContext: {
      employeeId: 'EMP-1006',
      name: 'Sanjay Patel',
      role: 'Sales Manager',
      department: 'Sales',
      declaredScope: 'region:West',
      violation: 'Attempted query of 5 accounts in region East'
    },
    summary: 'West Regional Sales Manager Sanjay Patel attempted to access customer accounts located in East region. Server-side scope enforcement rejected queries and raised elevated alert.',
    assignedTo: 'Regional Compliance Officer'
  },
  {
    id: 'alt-9821',
    title: 'BOLA / IDOR High-Volume Exploitation on /api/v2/users/{id}/financial-profile',
    severity: 'critical',
    category: 'BOLA',
    status: 'active',
    timestamp: '2026-10-13T22:24:18Z',
    targetEndpoint: '/api/v2/users/{id}/financial-profile',
    targetMethod: 'GET',
    actorIp: '194.26.29.112',
    actorCountry: 'Netherlands (Tor / Datacenter)',
    actorFingerprint: 'JA3: 771,4865-4866-4867,0-23-65281-10-11,29-23-24,0',
    owaspCategory: 'API1:2023 - Broken Object Level Authorization',
    requestCount: 142,
    blastRadius: '42 VIP Financial Records Exfiltrated',
    summary: 'Single authenticated session token sequentially tampered user UUIDs across 142 consecutive requests, successfully retrieving 42 unmasked customer profiles with SSNs and routing numbers.',
    assignedTo: 'SOC Lead Analyst (Alex Vance)',
  },
  {
    id: 'alt-9820',
    title: 'Shadow API Discovery & Unauthorized Secret Scraping on /internal/v1/debug/tokens',
    severity: 'critical',
    category: 'Shadow API Access',
    status: 'active',
    timestamp: '2026-10-13T22:25:01Z',
    targetEndpoint: '/internal/v1/debug/tokens',
    targetMethod: 'GET',
    actorIp: '194.26.29.112',
    actorCountry: 'Netherlands (Tor / Datacenter)',
    actorFingerprint: 'JA3: 771,4865-4866-4867,0-23-65281-10-11,29-23-24,0',
    owaspCategory: 'API9:2023 - Improper Inventory Management',
    requestCount: 15,
    blastRadius: 'Master Admin Token Ingestion Risk',
    summary: 'Actor probed undocumented internal endpoint and retrieved master JWT debug signatures without providing any bearer token.',
    assignedTo: 'SecOps Team',
  },
  {
    id: 'alt-9819',
    title: 'Distributed Credential Stuffing Attack Burst against /api/v1/auth/login',
    severity: 'high',
    category: 'Credential Stuffing',
    status: 'investigating',
    timestamp: '2026-10-13T22:21:40Z',
    targetEndpoint: '/api/v1/auth/login',
    targetMethod: 'POST',
    actorIp: '185.220.101.5',
    actorCountry: 'Germany (Exit Relay)',
    actorFingerprint: 'JA3: e7d705a3286e19ea42f587b344ee6865',
    owaspCategory: 'API2:2023 - Broken Authentication',
    requestCount: 1240,
    blastRadius: '12 accounts locked due to brute force protection',
    summary: 'High-frequency burst of POST requests testing credential pairs from leaked breaches across 35 revolving IP proxies.',
    assignedTo: 'Automated Bot Mitigation',
  },
  {
    id: 'alt-9818',
    title: 'BOPLA / Mass Assignment Exploit Attempt on /api/v1/users/{id}/profile',
    severity: 'high',
    category: 'Mass Assignment',
    status: 'active',
    timestamp: '2026-10-13T22:18:22Z',
    targetEndpoint: '/api/v1/users/{id}/profile',
    targetMethod: 'PUT',
    actorIp: '45.154.255.89',
    actorCountry: 'Russia (Bulletproof ASN 49304)',
    actorFingerprint: 'JA3: b32309a26ce51605dea1036d1a3d0ebb',
    owaspCategory: 'API3:2023 - Broken Object Property Level Auth',
    requestCount: 28,
    blastRadius: 'Attempted privilege escalation to "role": "SUPERADMIN"',
    summary: 'Injected non-whitelisted payload properties ("role": "SYSTEM_ADMIN", "is_verified": true) during normal user profile updates.',
    assignedTo: 'SOC Tier 2 Analyst',
  },
  {
    id: 'alt-9817',
    title: 'Zombie API Invocation: /v1/legacy/export/customers.csv Attempted Dump',
    severity: 'critical',
    category: 'Zombie API Access',
    status: 'mitigated',
    timestamp: '2026-10-13T22:15:30Z',
    targetEndpoint: '/v1/legacy/export/customers.csv',
    targetMethod: 'GET',
    actorIp: '91.240.118.23',
    actorCountry: 'Seychelles',
    actorFingerprint: 'JA3: 4d28430a6e033e08f5d023b7a58a7042',
    owaspCategory: 'API9:2023 - Improper Inventory Management',
    requestCount: 3,
    blastRadius: 'Export blocked by WAF Virtual Patch',
    summary: 'Deprecated CRM customer dump endpoint was hit with obsolete credentials. Successfully blocked at WAF ingress.',
    assignedTo: 'SecOps Auto-Defense',
    mitigatedAt: '2026-10-13T22:16:02Z',
  },
];

let trafficAnalytics = {
  timeSeries: [
    { timestamp: '21:00', totalRps: 280, cleanRps: 275, maliciousRps: 5, p50Latency: 42, p95Latency: 110, errorRate4xx: 1.1, errorRate5xx: 0.1 },
    { timestamp: '21:15', totalRps: 310, cleanRps: 302, maliciousRps: 8, p50Latency: 45, p95Latency: 118, errorRate4xx: 1.4, errorRate5xx: 0.1 },
    { timestamp: '21:30', totalRps: 340, cleanRps: 328, maliciousRps: 12, p50Latency: 48, p95Latency: 125, errorRate4xx: 2.0, errorRate5xx: 0.2 },
    { timestamp: '21:45', totalRps: 385, cleanRps: 350, maliciousRps: 35, p50Latency: 52, p95Latency: 140, errorRate4xx: 3.8, errorRate5xx: 0.3 },
    { timestamp: '22:00', totalRps: 450, cleanRps: 370, maliciousRps: 80, p50Latency: 64, p95Latency: 195, errorRate4xx: 6.5, errorRate5xx: 0.8 },
    { timestamp: '22:15', totalRps: 520, cleanRps: 390, maliciousRps: 130, p50Latency: 78, p95Latency: 240, errorRate4xx: 9.8, errorRate5xx: 1.2 },
    { timestamp: '22:25', totalRps: 480, cleanRps: 365, maliciousRps: 115, p50Latency: 72, p95Latency: 220, errorRate4xx: 8.2, errorRate5xx: 0.9 },
  ],
  statusCodes: [
    { code: '200 OK', count: 842100, percentage: 84.2 },
    { code: '201 Created', count: 65400, percentage: 6.5 },
    { code: '400 Bad Request', count: 12400, percentage: 1.2 },
    { code: '401 Unauthorized', count: 34100, percentage: 3.4 },
    { code: '403 Forbidden (Blocked)', count: 28900, percentage: 2.9 },
    { code: '404 Not Found', count: 9800, percentage: 1.0 },
    { code: '429 Rate Limited', count: 7600, percentage: 0.8 },
    { code: '500 Internal Error', count: 2100, percentage: 0.2 },
  ],
  topActors: [
    { ip: '194.26.29.112', country: 'Netherlands', requests: 1840, maliciousPercentage: 94.2, status: 'active', threatLabel: 'Tor Exit Node / BOLA Exfiltrator' },
    { ip: '185.220.101.5', country: 'Germany', requests: 1240, maliciousPercentage: 98.1, status: 'active', threatLabel: 'Credential Stuffing Botnet' },
    { ip: '45.154.255.89', country: 'Russia', requests: 480, maliciousPercentage: 86.5, status: 'active', threatLabel: 'BOPLA Exploit Probe' },
    { ip: '198.51.100.42', country: 'United States', requests: 12500, maliciousPercentage: 0.4, status: 'monitored', threatLabel: 'Legitimate Mobile Client Gateway' },
    { ip: '91.240.118.23', country: 'Seychelles', requests: 120, maliciousPercentage: 100.0, status: 'blocked', threatLabel: 'Zombie API Scraper (Blocked)' },
  ],
  topTargetEndpoints: [
    { path: '/api/v2/users/{id}/financial-profile', method: 'GET', rps: 42.5, errorRate: 14.8, maliciousRps: 28.2 },
    { path: '/api/v1/auth/login', method: 'POST', rps: 154.2, errorRate: 22.1, maliciousRps: 64.0 },
    { path: '/internal/v1/debug/tokens', method: 'GET', rps: 8.2, errorRate: 0.0, maliciousRps: 8.2 },
    { path: '/api/v1/users/{id}/profile', method: 'PUT', rps: 65.1, errorRate: 7.4, maliciousRps: 12.1 },
    { path: '/api/v2/catalog/search', method: 'GET', rps: 110.8, errorRate: 0.8, maliciousRps: 1.2 },
  ],
  geoDistribution: [
    { country: 'United States', cleanRequests: 420000, maliciousRequests: 1200 },
    { country: 'Netherlands', cleanRequests: 18000, maliciousRequests: 8900 },
    { country: 'Germany', cleanRequests: 45000, maliciousRequests: 7400 },
    { country: 'Russia', cleanRequests: 4000, maliciousRequests: 9200 },
    { country: 'United Kingdom', cleanRequests: 85000, maliciousRequests: 800 },
  ],
};

let blockedActors = new Set();

// Investigation Datastore by alert ID
const investigations = {
  'alt-9821': {
    alertId: 'alt-9821',
    actor: {
      id: 'act-19426',
      ip: '194.26.29.112',
      country: 'Netherlands',
      city: 'Amsterdam',
      isp: 'Tor Network Exit Node / Datacenter ASN 49505',
      asn: 'AS49505 (HostRoyale Hosting B.V.)',
      reputationScore: 98,
      threatLevel: 'Malicious Bot',
      ja3Fingerprint: '771,4865-4866-4867,0-23-65281-10-11,29-23-24,0',
      ja4Fingerprint: 't13d1516h2_8daaf6152771_b4bfa4a34b4c',
      userAgent: 'python-requests/2.31.0 (Automated Harvester)',
      firstSeen: '2026-10-13T22:10:14Z',
      lastSeen: '2026-10-13T22:27:12Z',
      totalRequests: 214,
      blockedRequests: 32,
      isBlocked: false,
    },
    timeline: [
      {
        id: 'tl-1',
        timestamp: '22:10:14',
        phase: 'Reconnaissance',
        title: 'Initial Entrypoint & Token Acquisition',
        description: 'Actor authenticated with low-privilege test account test_user_42@tempmail.com and obtained standard JWT token.',
        severity: 'info',
        endpoint: 'POST /api/v1/auth/login',
        indicators: ['Disposable Email Domain', 'Tor Exit IP (194.26.29.112)', 'Headless Python UA'],
      },
      {
        id: 'tl-2',
        timestamp: '22:15:02',
        phase: 'Vulnerability Probe',
        title: 'Shadow Route Fingerprinting',
        description: 'Actor scanned undocumented internal routes, locating exposed debug endpoint /internal/v1/debug/tokens.',
        severity: 'medium',
        endpoint: 'GET /internal/v1/debug/tokens',
        indicators: ['Brute-force path dictionary scan', 'HTTP 200 on unauthenticated route'],
      },
      {
        id: 'tl-3',
        timestamp: '22:20:44',
        phase: 'Exploitation',
        title: 'First BOLA Parameter Manipulation Test',
        description: 'Actor used own JWT token to request financial profile for victim usr_84920482. System returned 200 OK without verifying ownership!',
        severity: 'critical',
        endpoint: 'GET /api/v2/users/usr_84920482/financial-profile',
        indicators: ['JWT Token Subject mismatch', 'Target ID tamper', 'HTTP 200 Data Leak'],
      },
      {
        id: 'tl-4',
        timestamp: '22:24:18',
        phase: 'Data Exfiltration',
        title: 'Automated High-Rate Scripted Exfiltration',
        description: 'Actor initiated rapid multi-threaded loop iterating user IDs usr_84920480 through usr_84920622, exfiltrating 42 complete financial records.',
        severity: 'critical',
        endpoint: 'GET /api/v2/users/{id}/financial-profile?include_raw_records=true',
        indicators: ['142 requests in 25 seconds', '42 unmasked SSNs exfiltrated', 'Undocumented query param used'],
      },
      {
        id: 'tl-5',
        timestamp: '22:27:00',
        phase: 'Mitigation',
        title: 'Behavioral Anomaly Engine Triggered',
        description: 'CyberCup Real-Time Engine classified behavior as OWASP API1:2023 Violation. Alert #alt-9821 raised to SOC.',
        severity: 'high',
        endpoint: 'SOC Defense Console',
        indicators: ['Threat Score 98/100', 'Virtual Patch Recommendation Ready'],
      },
    ],
    rawRequests: [
      {
        id: 'req-001',
        timestamp: '2026-10-13T22:24:18.102Z',
        method: 'GET',
        url: 'https://api.cybercup.corp/api/v2/users/usr_84920482/financial-profile?include_raw_records=true',
        headers: {
          'Host': 'api.cybercup.corp',
          'User-Agent': 'python-requests/2.31.0',
          'Accept': '*/*',
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMTAwMDEiLCJyb2xlIjoidXNlciJ9.K78_sample_signature_jwt',
          'X-Forwarded-For': '194.26.29.112',
        },
        queryParams: { 'include_raw_records': 'true' },
        body: null,
        responseStatus: 200,
        responseHeaders: {
          'Content-Type': 'application/json',
          'Content-Length': '842',
          'X-RateLimit-Remaining': '472',
        },
        responseBody: {
          account_id: 'usr_84920482',
          full_name: 'Alexander M. Wright',
          ssn: '482-90-1193',
          credit_score: 792,
          routing_number: '121000358',
          account_balance: 142850.45,
          email: 'a.wright@enterprise-corp.com',
          active_loans: [{ loan_id: 'ln-9912', amount: 35000.0, status: 'current' }],
        },
        latencyMs: 38,
        anomalies: [
          'JWT sub (usr_10001) does NOT match URL resource (usr_84920482)',
          'Unmasked SSN (482-90-1193) returned in cleartext JSON',
          'Undocumented parameter include_raw_records=true triggered',
        ],
        curlCommand: `curl -X GET "https://api.cybercup.corp/api/v2/users/usr_84920482/financial-profile?include_raw_records=true" \\\n  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMTAwMDEiLCJyb2xlIjoidXNlciJ9.K78_sample_signature_jwt" \\\n  -H "User-Agent: python-requests/2.31.0" \\\n  -H "X-Forwarded-For: 194.26.29.112"`,
      },
      {
        id: 'req-002',
        timestamp: '2026-10-13T22:24:18.284Z',
        method: 'GET',
        url: 'https://api.cybercup.corp/api/v2/users/usr_84920483/financial-profile?include_raw_records=true',
        headers: {
          'Host': 'api.cybercup.corp',
          'User-Agent': 'python-requests/2.31.0',
          'Accept': '*/*',
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMTAwMDEiLCJyb2xlIjoidXNlciJ9.K78_sample_signature_jwt',
          'X-Forwarded-For': '194.26.29.112',
        },
        queryParams: { 'include_raw_records': 'true' },
        body: null,
        responseStatus: 200,
        responseHeaders: {
          'Content-Type': 'application/json',
          'Content-Length': '810',
          'X-RateLimit-Remaining': '471',
        },
        responseBody: {
          account_id: 'usr_84920483',
          full_name: 'Elena Rostova',
          ssn: '591-12-8820',
          credit_score: 815,
          routing_number: '121000358',
          account_balance: 298100.0,
          email: 'e.rostova@global-fund.ch',
          active_loans: [],
        },
        latencyMs: 34,
        anomalies: [
          'Sequential ID step manipulation (+1 iteration)',
          'Unmasked SSN (591-12-8820) returned in cleartext JSON',
        ],
        curlCommand: `curl -X GET "https://api.cybercup.corp/api/v2/users/usr_84920483/financial-profile?include_raw_records=true" \\\n  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMTAwMDEiLCJyb2xlIjoidXNlciJ9.K78_sample_signature_jwt" \\\n  -H "User-Agent: python-requests/2.31.0"`,
      },
    ],
    actorOtherActivity: {
      targetedEndpoints: [
        {
          endpoint: '/api/v1/auth/login',
          method: 'POST',
          requestCount: 3,
          statusPattern: '200 OK (Legitimate Auth)',
          firstSeen: '22:10:14',
          lastSeen: '22:10:16',
          exploitType: 'Credential Token Harvester',
        },
        {
          endpoint: '/internal/v1/debug/tokens',
          method: 'GET',
          requestCount: 15,
          statusPattern: '200 OK (Unauthenticated Access)',
          firstSeen: '22:15:02',
          lastSeen: '22:15:40',
          exploitType: 'Shadow API Reconnaissance',
        },
        {
          endpoint: '/api/v2/users/{id}/financial-profile',
          method: 'GET',
          requestCount: 142,
          statusPattern: '200 OK (BOLA / IDOR Mass Harvest)',
          firstSeen: '22:20:44',
          lastSeen: '22:24:45',
          exploitType: 'BOLA Exploit & PII Exfiltration',
        },
        {
          endpoint: '/api/v1/transfers/wire',
          method: 'POST',
          requestCount: 4,
          statusPattern: '403 Forbidden (Blocked by mTLS)',
          firstSeen: '22:26:10',
          lastSeen: '22:26:15',
          exploitType: 'Unauthorized Financial Execution Attempt',
        },
      ],
      otherAlerts: [
        {
          id: 'alt-9820',
          title: 'Shadow API Discovery & Unauthorized Secret Scraping on /internal/v1/debug/tokens',
          severity: 'critical',
          timestamp: '2026-10-13T22:25:01Z',
        },
      ],
      attackPatternSummary: 'Attacker combined legitimate credential acquisition with shadow API enumeration to identify internal architecture, then exploited an authorization bypass (BOLA) to exfiltrate 42 VIP customer records. Final stage attempted wire transfers but was halted by mTLS controls.',
      blastRadiusEstimate: '42 High-Net-Worth customer identities, SSNs, credit scores, and bank routing numbers compromised.',
    },
  },
};

// ======================== REST API ROUTES ========================

// 1. Health check
app.get('/api/v1/health', (req, res) => {
  res.json({
    status: 'online',
    timestamp: new Date().toISOString(),
    service: 'CyberCup API Security Intelligence Engine',
    version: '2.4.0',
    mode: 'live-defense-active',
  });
});

// 2. Overview / Posture
app.get('/api/v1/overview/posture', (req, res) => {
  res.json(overviewPosture);
});

// 3. Searchable Inventory
app.get('/api/v1/inventory', (req, res) => {
  let results = [...inventory];
  const { search, status, minRisk, method, environment } = req.query;

  if (search) {
    const s = search.toLowerCase();
    results = results.filter(
      item =>
        item.path.toLowerCase().includes(s) ||
        item.service.toLowerCase().includes(s) ||
        item.tags.some(t => t.toLowerCase().includes(s))
    );
  }

  if (status && status !== 'all') {
    results = results.filter(item => item.status === status);
  }

  if (method && method !== 'all') {
    results = results.filter(item => item.method === method);
  }

  if (environment && environment !== 'all') {
    results = results.filter(item => item.environment === environment);
  }

  if (minRisk) {
    results = results.filter(item => item.riskScore >= parseInt(minRisk, 10));
  }

  res.json(results);
});

// 4. API Detail with Risk Breakdown
app.get('/api/v1/inventory/:id', (req, res) => {
  const item = inventory.find(i => i.id === req.params.id);
  if (!item) {
    return res.status(404).json({ error: 'Endpoint not found in inventory' });
  }
  res.json(item);
});

// 5. Alerts List
app.get('/api/v1/alerts', (req, res) => {
  let results = [...alerts];
  const { severity, status, category } = req.query;

  if (severity && severity !== 'all') {
    results = results.filter(a => a.severity === severity);
  }
  if (status && status !== 'all') {
    results = results.filter(a => a.status === status);
  }
  if (category && category !== 'all') {
    results = results.filter(a => a.category.toLowerCase().includes(category.toLowerCase()));
  }

  res.json(results);
});

app.get('/api/v1/alerts/:id', (req, res) => {
  const alert = alerts.find(a => a.id === req.params.id);
  if (!alert) {
    return res.status(404).json({ error: 'Alert not found' });
  }
  res.json(alert);
});

// 6. Traffic Analytics
app.get('/api/v1/analytics/traffic', (req, res) => {
  res.json(trafficAnalytics);
});

// 7. Investigation View drill-down
app.get('/api/v1/investigation/:alertId', (req, res) => {
  const { alertId } = req.params;
  const alert = alerts.find(a => a.id === alertId);

  if (!alert) {
    return res.status(404).json({ error: 'Alert not found for investigation' });
  }

  // If specific investigation exists, use it, else synthesize dynamically
  let invData = investigations[alertId];
  if (!invData) {
    invData = {
      alert,
      actor: {
        id: `act-${alert.actorIp.replace(/[^0-9]/g, '').slice(0, 6)}`,
        ip: alert.actorIp,
        country: alert.actorCountry,
        city: 'Detected Geo',
        isp: 'Suspected Botnet Infrastructure',
        asn: 'AS-DYNAMIC-DETECTED',
        reputationScore: alert.severity === 'critical' ? 95 : 75,
        threatLevel: 'Malicious Bot',
        ja3Fingerprint: alert.actorFingerprint,
        ja4Fingerprint: 't13d1516h2_synthetic_probe',
        userAgent: 'python-requests/2.31.0',
        firstSeen: alert.timestamp,
        lastSeen: new Date().toISOString(),
        totalRequests: alert.requestCount,
        blockedRequests: 0,
        isBlocked: blockedActors.has(alert.actorIp),
      },
      timeline: [
        {
          id: 'tl-dyn-1',
          timestamp: '22:15:00',
          phase: 'Reconnaissance',
          title: `Initial Probe on ${alert.targetEndpoint}`,
          description: `Actor initiated anomalous query traffic targeting ${alert.targetEndpoint}`,
          severity: 'info',
          endpoint: alert.targetEndpoint,
          indicators: ['Automated request cadence', 'Unrecognized header fingerprint'],
        },
        {
          id: 'tl-dyn-2',
          timestamp: '22:24:00',
          phase: 'Exploitation',
          title: `${alert.category} Anomaly Threshold Exceeded`,
          description: alert.summary,
          severity: alert.severity,
          endpoint: alert.targetEndpoint,
          indicators: [alert.owaspCategory, `Blast radius: ${alert.blastRadius}`],
        },
      ],
      rawRequests: [
        {
          id: 'req-dyn-1',
          timestamp: alert.timestamp,
          method: alert.targetMethod,
          url: `https://api.cybercup.corp${alert.targetEndpoint}`,
          headers: {
            'Host': 'api.cybercup.corp',
            'User-Agent': 'python-requests/2.31.0',
            'X-Forwarded-For': alert.actorIp,
          },
          queryParams: {},
          body: null,
          responseStatus: 200,
          responseHeaders: { 'Content-Type': 'application/json' },
          responseBody: { message: 'Sample intercepted response matching anomalous request' },
          latencyMs: 45,
          anomalies: [alert.owaspCategory, 'Pattern mismatch detected by ML baseline'],
          curlCommand: `curl -X ${alert.targetMethod} "https://api.cybercup.corp${alert.targetEndpoint}" -H "X-Forwarded-For: ${alert.actorIp}"`,
        },
      ],
      actorOtherActivity: {
        targetedEndpoints: [
          {
            endpoint: alert.targetEndpoint,
            method: alert.targetMethod,
            requestCount: alert.requestCount,
            statusPattern: '200 OK / Anomaly',
            firstSeen: alert.timestamp,
            lastSeen: new Date().toISOString(),
            exploitType: alert.category,
          },
        ],
        otherAlerts: [],
        attackPatternSummary: alert.summary,
        blastRadiusEstimate: alert.blastRadius,
      },
    };
  }

  // Update actor blocked status
  if (invData.actor) {
    invData.actor.isBlocked = blockedActors.has(invData.actor.ip);
  }

  res.json(invData);
});

// 8. Actor Profile
app.get('/api/v1/actors/:actorId', (req, res) => {
  const inv = Object.values(investigations).find(i => i.actor && i.actor.id === req.params.actorId);
  if (!inv) {
    return res.status(404).json({ error: 'Actor profile not found' });
  }
  res.json(inv.actor);
});

// 9. Action: Block Actor IP
app.post('/api/v1/actions/block-actor', (req, res) => {
  const { ip, reason } = req.body;
  if (!ip) {
    return res.status(400).json({ error: 'Actor IP required' });
  }

  blockedActors.add(ip);

  // Update traffic analytics status
  const actorEntry = trafficAnalytics.topActors.find(a => a.ip === ip);
  if (actorEntry) {
    actorEntry.status = 'blocked';
  }

  // Increment blocked count
  overviewPosture.kpis.blockedAttacks24h += 1;

  res.json({
    success: true,
    message: `Actor IP ${ip} successfully blocked globally across WAF & API Gateways`,
    ip,
    action: 'GLOBAL_IP_DENY',
    enforcementLatencyMs: 12,
    timestamp: new Date().toISOString(),
  });
});

// 10. Action: Quarantine API Endpoint
app.post('/api/v1/actions/quarantine-api', (req, res) => {
  const { apiId, mode } = req.body;
  const item = inventory.find(i => i.id === apiId);
  if (!item) {
    return res.status(404).json({ error: 'API not found' });
  }

  item.mitigationStatus.quarantined = true;
  item.mitigationStatus.virtualPatched = true;

  res.json({
    success: true,
    message: `API endpoint ${item.path} quarantined. Virtual patch active at edge gateway.`,
    apiId,
    endpoint: item.path,
    status: 'QUARANTINED',
    timestamp: new Date().toISOString(),
  });
});

// 11. Action: Mitigate Alert
app.post('/api/v1/actions/mitigate-alert', (req, res) => {
  const { alertId, resolutionNote } = req.body;
  const alert = alerts.find(a => a.id === alertId);
  if (!alert) {
    return res.status(404).json({ error: 'Alert not found' });
  }

  alert.status = 'mitigated';
  alert.mitigatedAt = new Date().toISOString();
  overviewPosture.kpis.criticalAlerts = Math.max(0, overviewPosture.kpis.criticalAlerts - 1);
  overviewPosture.overallScore = Math.min(100, overviewPosture.overallScore + 4);

  res.json({
    success: true,
    message: `Alert ${alertId} marked as mitigated. Posture score updated.`,
    alert,
  });
});

// 12. Simulate Live Attack (Key feature for 5-minute live demo!)
app.post('/api/v1/simulate-attack', (req, res) => {
  const attackType = req.body.type || 'bola';
  const newAlertId = `alt-${Math.floor(1000 + Math.random() * 9000)}`;

  let simulatedAlert;

  if (attackType === 'bola') {
    simulatedAlert = {
      id: newAlertId,
      title: `LIVE ATTACK: BOLA Exfiltration Burst on /api/v2/users/{id}/financial-profile`,
      severity: 'critical',
      category: 'BOLA',
      status: 'active',
      timestamp: new Date().toISOString(),
      targetEndpoint: '/api/v2/users/{id}/financial-profile',
      targetMethod: 'GET',
      actorIp: '194.26.29.112',
      actorCountry: 'Netherlands (Tor / Datacenter)',
      actorFingerprint: 'JA3: 771,4865-4866-4867,0-23-65281-10-11,29-23-24,0',
      owaspCategory: 'API1:2023 - Broken Object Level Authorization',
      requestCount: 85,
      blastRadius: '28 Customer Financial Records Harvested',
      summary: 'LIVE SIMULATION: Automated script cycling through customer IDs via compromised JWT credential. Immediate authorization bypass detected.',
      assignedTo: 'SOC Live Auto-Response',
    };
  } else {
    simulatedAlert = {
      id: newAlertId,
      title: `LIVE ATTACK: Unauthorized Secret Extraction on /internal/v1/debug/tokens`,
      severity: 'critical',
      category: 'Shadow API Access',
      status: 'active',
      timestamp: new Date().toISOString(),
      targetEndpoint: '/internal/v1/debug/tokens',
      targetMethod: 'GET',
      actorIp: '194.26.29.112',
      actorCountry: 'Netherlands (Tor / Datacenter)',
      actorFingerprint: 'JA3: 771,4865-4866-4867,0-23-65281-10-11,29-23-24,0',
      owaspCategory: 'API9:2023 - Improper Inventory Management',
      requestCount: 22,
      blastRadius: 'Master Admin Token Compromise Risk',
      summary: 'LIVE SIMULATION: Unregistered shadow endpoint probed with no authentication headers.',
      assignedTo: 'SOC Live Auto-Response',
    };
  }

  alerts.unshift(simulatedAlert);
  overviewPosture.kpis.criticalAlerts += 1;
  overviewPosture.overallScore = Math.max(40, overviewPosture.overallScore - 3);

  // Add traffic burst to time series
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  trafficAnalytics.timeSeries.push({
    timestamp: timeStr,
    totalRps: 610,
    cleanRps: 380,
    maliciousRps: 230,
    p50Latency: 92,
    p95Latency: 280,
    errorRate4xx: 12.4,
    errorRate5xx: 1.8,
  });

  res.json({
    success: true,
    message: 'Live attack simulation injected successfully',
    alert: simulatedAlert,
    investigationUrl: `/api/v1/investigation/${newAlertId}`,
  });
});

app.listen(PORT, () => {
  console.log(`[CyberCup Defense Backend] Running on http://localhost:${PORT}`);
  console.log(`[REST Endpoints active] /api/v1/overview/posture, /api/v1/inventory, /api/v1/alerts, /api/v1/analytics/traffic, /api/v1/investigation/:alertId`);
});
