/**
 * CC6-IC07: API Discovery, Security and Abuse Prevention
 * Frozen Data Contracts strictly enforced.
 */

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
export type AuthType = 'jwt' | 'oauth2' | 'api_key' | 'basic' | 'none';

// ==========================================
// 1. REQUEST LOG RECORD
// ==========================================
export interface RequestLogRecord {
  request_id: string;
  timestamp: string; // ISO 8601
  method: HttpMethod;
  raw_path: string;
  path_template: string;
  query_params: Record<string, any> | string[];
  status_code: number;
  response_size: number;
  request_size: number;
  latency_ms: number;
  client_ip: string;
  user_agent: string;
  auth_type: string;
  token_id: string | null;
  user_id: string | null;
  object_ids: string[];
  sensitive_types: string[]; // ["PAN", "Aadhaar", "phone", "email"]
  label?: string; // Ground-truth label, only visible on Evaluation page
}

// ==========================================
// 2. ALERT
// ==========================================
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical' | 'informational';
export type AlertStatus = 'open' | 'investigating' | 'resolved';
export type AlertType = 'BOLA' | 'token_misuse' | 'scraping' | 'unauthorized_access' | 'brute_force' | string;

export interface Alert {
  alert_id: string;
  type: AlertType;
  owasp: string; // e.g. "API1:2023 BOLA"
  severity: AlertSeverity;
  api: string; // e.g. "GET /accounts/{id}"
  actor: string; // user_id, token_id, or client_ip
  first_seen: string;
  last_seen: string;
  status: AlertStatus;
  reason: string;
  request_ids: string[];
  recommendation: string;
  identity_context?: any;
  reasoning_chain?: string[];
  priority_tag?: string;
  is_downgraded?: boolean;
  elevated_priority?: boolean;
}

// ==========================================
// 3. API INVENTORY ITEM
// ==========================================
export type ApiInventoryStatus = 'documented' | 'shadow' | 'zombie' | 'unmanaged' | 'unused_documented';
export type ApiExposure = 'public' | 'internal';

export interface ApiParameter {
  name: string;
  in: 'path' | 'query' | 'header' | 'body';
  type: string;
  required: boolean;
}

export interface ApiInventoryItem {
  api_id: string;
  method: HttpMethod;
  path_template: string;
  auth_type: string;
  parameters: ApiParameter[];
  sensitive_types: string[]; // ["PAN", "Aadhaar", "phone", "email"]
  status: ApiInventoryStatus;
  first_seen: string;
  last_seen: string;
  request_count: number;
  exposure: ApiExposure;
  risk_score: number; // 0-100
}

// ==========================================
// 4. RISK SCORE & BREAKDOWN
// Categories: Exposure (0-40), Data Sensitivity (0-25), Behavior (0-20), Security Events (0-15)
// ==========================================
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface RiskBreakdownFactor {
  factor: 'Exposure' | 'Data Sensitivity' | 'Behavior' | 'Security Events' | string;
  points: number;
  max_points: number;
  reason: string;
}

export interface RiskScore {
  api_id: string;
  score: number; // 0-100
  level: RiskLevel;
  breakdown: RiskBreakdownFactor[];
}

// ==========================================
// 5. BASELINE
// Metrics: rate | payload_size | unique_callers | hourly_distribution
// ==========================================
export type BaselineMetric = 'rate' | 'payload_size' | 'unique_callers' | 'hourly_distribution';

export interface Baseline {
  api_id: string;
  metric: BaselineMetric;
  baseline_values: any;
  live_values: any;
}

// ==========================================
// 6. EVALUATION
// ==========================================
export interface EvaluationScenario {
  scenario: string;
  recall: number;
  detected: number;
  total: number;
  mean_ttd_s: number;
}

export interface EvaluationData {
  overall: {
    detection_rate: number;
    fp_rate: number;
    precision: number;
    f1: number;
    mean_time_to_detect_s: number;
  };
  per_scenario: EvaluationScenario[];
  confusion_matrix: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
  before_after_tuning?: {
    metric: string;
    before: number;
    after: number;
  }[];
  known_limitations?: string[];
}

// ==========================================
// REST ENDPOINT RESPONSES
// ==========================================

export interface PostureResponse {
  posture_score: number; // 0-100
  posture_explanation: string;
  total_apis: number;
  counts_by_status: Record<ApiInventoryStatus, number>;
  alerts_by_severity: Record<AlertSeverity, number>;
  alerts_by_type: Record<string, number>;
  top_risky_apis: {
    api_id: string;
    method: string;
    path_template: string;
    risk_score: number;
    reason_chip: string;
  }[];
  requests_over_time: {
    timestamp: string;
    count: number;
  }[];
}

export interface TrafficStats {
  window: string;
  requests_over_time: {
    timestamp: string;
    requests_per_min: number;
    error_rate: number;
  }[];
  error_rates: {
    rate_4xx: number;
    rate_5xx: number;
  };
  latency_percentiles: {
    p50: number;
    p90: number;
    p99: number;
  };
  top_consumers: {
    actor: string;
    requests: number;
    error_rate: number;
  }[];
  top_endpoints: {
    api: string;
    requests: number;
    error_rate: number;
  }[];
  status_codes: {
    code: string;
    count: number;
    percentage: number;
  }[];
  ip_geo_breakdown: {
    country: string;
    ip_count: number;
    requests: number;
  }[];
  auth_split: {
    auth_type: string;
    percentage: number;
  }[];
}

export interface ActorActivityResponse {
  actor: string;
  total_requests: number;
  distinct_endpoints: number;
  requests: RequestLogRecord[];
  endpoints_hit: {
    path_template: string;
    method: string;
    count: number;
  }[];
  ip_changes: string[];
  user_agents: string[];
}

export interface ApiDetailResponse {
  inventory_item: ApiInventoryItem;
  risk_breakdown: RiskScore;
  baselines: Baseline[];
  related_alerts: Alert[];
}
