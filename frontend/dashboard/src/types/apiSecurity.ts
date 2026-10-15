// TypeScript definitions for CyberCup API Security Posture Management Platform

export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type ApiStatus = 'managed' | 'shadow' | 'zombie' | 'deprecated';
export type AlertStatus = 'active' | 'investigating' | 'mitigated' | 'false_positive';
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface OverviewPosture {
  overallScore: number;
  grade: string;
  riskSummary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  postureBreakdown: {
    category: string;
    score: number;
    status: 'good' | 'warning' | 'critical';
    issuesCount: number;
    description: string;
  }[];
  kpis: {
    totalApis: number;
    shadowApis: number;
    zombieApis: number;
    criticalAlerts: number;
    sensitiveDataExposures: number;
    blockedAttacks24h: number;
    trafficRps: number;
    dataLossPreventionSaves: number;
  };
  owaspTop10Distribution: {
    code: string;
    name: string;
    shortName: string;
    count: number;
    severity: Severity;
  }[];
  riskTrend: {
    date: string;
    critical: number;
    high: number;
    medium: number;
    low: number;
    postureScore: number;
  }[];
  threatGeos: {
    country: string;
    code: string;
    attacks: number;
    percentage: number;
  }[];
}

export interface ApiInventoryItem {
  id: string;
  method: HttpMethod;
  path: string;
  service: string;
  host: string;
  environment: 'production' | 'staging' | 'internal';
  status: ApiStatus;
  riskScore: number;
  riskLevel: Severity;
  authType: string;
  piiDetected: string[];
  rps: number;
  lastSeen: string;
  specDrift: boolean;
  tags: string[];
  activeThreatCount: number;
}

export interface RiskFactor {
  name: string;
  score: number;
  impact: string;
  owasp: string;
  mitigated: boolean;
}

export interface ApiParameter {
  name: string;
  in: 'path' | 'query' | 'header' | 'body';
  type: string;
  required: boolean;
  sensitive: boolean;
  description: string;
}

export interface ApiDetail extends ApiInventoryItem {
  riskBreakdown: {
    factors: RiskFactor[];
    remediationGuidance: string[];
  };
  parameters: ApiParameter[];
  samplePayloads: {
    request: Record<string, any>;
    response: Record<string, any>;
  };
  schemaDrift: {
    hasDrift: boolean;
    undocumentedFields: string[];
    missingRequiredFields: string[];
    lastSpecSync: string;
  };
  mitigationStatus: {
    quarantined: boolean;
    virtualPatched: boolean;
    wafRuleActive: boolean;
  };
}

export interface SecurityAlert {
  id: string;
  title: string;
  severity: Severity;
  category: string;
  status: AlertStatus;
  timestamp: string;
  targetEndpoint: string;
  targetMethod: HttpMethod;
  actorIp: string;
  actorCountry: string;
  actorFingerprint: string;
  owaspCategory: string;
  requestCount: number;
  blastRadius: string;
  summary: string;
  assignedTo: string;
  mitigatedAt?: string;
}

export interface TrafficDataPoint {
  timestamp: string;
  totalRps: number;
  cleanRps: number;
  maliciousRps: number;
  p50Latency: number;
  p95Latency: number;
  errorRate4xx: number;
  errorRate5xx: number;
}

export interface StatusCodeBreakdown {
  code: string;
  count: number;
  percentage: number;
}

export interface TopActorTraffic {
  ip: string;
  country: string;
  requests: number;
  maliciousPercentage: number;
  status: 'active' | 'blocked' | 'monitored';
  threatLabel: string;
}

export interface TrafficAnalytics {
  timeSeries: TrafficDataPoint[];
  statusCodes: StatusCodeBreakdown[];
  topActors: TopActorTraffic[];
  topTargetEndpoints: {
    path: string;
    method: HttpMethod;
    rps: number;
    errorRate: number;
    maliciousRps: number;
  }[];
  geoDistribution: {
    country: string;
    cleanRequests: number;
    maliciousRequests: number;
  }[];
}

export interface InvestigationTimelineEvent {
  id: string;
  timestamp: string;
  phase: 'Reconnaissance' | 'Vulnerability Probe' | 'Exploitation' | 'Data Exfiltration' | 'Mitigation';
  title: string;
  description: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  endpoint: string;
  indicators: string[];
}

export interface RawHttpRequestRecord {
  id: string;
  timestamp: string;
  method: HttpMethod;
  url: string;
  headers: Record<string, string>;
  queryParams: Record<string, string>;
  body: any;
  responseStatus: number;
  responseHeaders: Record<string, string>;
  responseBody: any;
  latencyMs: number;
  anomalies: string[];
  curlCommand: string;
}

export interface ActorProfile {
  id: string;
  ip: string;
  country: string;
  city: string;
  isp: string;
  asn: string;
  reputationScore: number;
  threatLevel: string;
  ja3Fingerprint: string;
  ja4Fingerprint: string;
  userAgent: string;
  firstSeen: string;
  lastSeen: string;
  totalRequests: number;
  blockedRequests: number;
  isBlocked: boolean;
}

export interface ActorTargetedEndpoint {
  endpoint: string;
  method: HttpMethod;
  requestCount: number;
  statusPattern: string;
  firstSeen: string;
  lastSeen: string;
  exploitType?: string;
}

export interface InvestigationData {
  alert: SecurityAlert;
  actor: ActorProfile;
  timeline: InvestigationTimelineEvent[];
  rawRequests: RawHttpRequestRecord[];
  actorOtherActivity: {
    targetedEndpoints: ActorTargetedEndpoint[];
    otherAlerts: {
      id: string;
      title: string;
      severity: Severity;
      timestamp: string;
    }[];
    attackPatternSummary: string;
    blastRadiusEstimate: string;
  };
}
