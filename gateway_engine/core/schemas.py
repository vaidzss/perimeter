"""
Pydantic v2 schemas for SentinelAPI Gateway and SOC Dashboard.
"""

import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    event_id: str
    timestamp: datetime.datetime
    method: str
    path: str
    normalized_path: Optional[str] = None
    query_params: str = ""
    request_headers: Dict[str, str] = Field(default_factory=dict)
    request_body: Optional[str] = None
    response_status: int
    response_headers: Dict[str, str] = Field(default_factory=dict)
    response_body: Optional[str] = None
    latency_ms: float
    client_ip: str
    user_agent: str
    jwt_sub: Optional[str] = None
    jwt_jti: Optional[str] = None
    jwt_account_id: Optional[str] = None
    jwt_role: Optional[str] = None
    x_truth: Optional[str] = None  # Ground-truth: benign, attack_bola, attack_scraping, attack_replay, attack_shadow
    mitigation_applied: str = "NONE"


class DiscoveredAPISchema(BaseModel):
    id: str
    method: str
    path: str
    normalized_path: str
    status: str  # DOCUMENTED, SHADOW, ZOMBIE
    service: str = "fintech-core"
    host: str = "api.fintech.mesh"
    risk_score: int = 0
    risk_level: str = "low"
    auth_type: str = "None"
    pii_detected: List[str] = Field(default_factory=list)
    rps: float = 0.0
    last_seen: Optional[datetime.datetime] = None
    spec_drift: bool = False
    tags: List[str] = Field(default_factory=list)
    active_threat_count: int = 0
    risk_reasons: List[str] = Field(default_factory=list)
    auto_swagger_spec: Dict[str, Any] = Field(default_factory=dict)
    quarantined: bool = False
    mask_pii: bool = False
    honeypot_bola: bool = False


class SecurityAlertSchema(BaseModel):
    id: str
    timestamp: datetime.datetime
    severity: str  # critical, high, medium, low
    category: str
    threat_actor_ip: str
    endpoint: str
    method: str
    status: str = "active"
    description: str
    owasp_category: str
    forensic_data: Dict[str, Any] = Field(default_factory=dict)


class ForensicLogSchema(BaseModel):
    id: str
    timestamp: datetime.datetime
    client_ip: str
    user_agent: str
    method: str
    path: str
    normalized_path: str
    query_params: str
    request_headers: Dict[str, str]
    response_status: int
    latency_ms: float
    jwt_sub: Optional[str] = None
    jwt_jti: Optional[str] = None
    x_truth: Optional[str] = None
    flagged_anomalies: List[str] = Field(default_factory=list)
    mitigation_action: str = "NONE"
    response_body_sample: Optional[str] = None


class MitigationActionRequest(BaseModel):
    action: str  # quarantine, mask_pii, honeypot_bola, block_ip, unblock_ip
    target: str  # api_id, route_path, or ip address
    value: bool = True
    reason: Optional[str] = None


class ConfusionMatrixMetrics(BaseModel):
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    total_evaluated: int = 0
    tpr: float = 0.0  # Recall / Detection Rate %
    fpr: float = 0.0  # False Positive Rate %
    precision: float = 0.0
    f1_score: float = 0.0
