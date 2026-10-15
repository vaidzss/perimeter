"""
Core Data Models for API Discovery, Shadow Detection & Runtime Abuse Prevention.
Adheres strictly to the CC6-IC07 Blueprint specifications and OWASP API Security Top 10 (2023).
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import time


class SpecDriftStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    SHADOW = "SHADOW"
    ZOMBIE = "ZOMBIE"


class PIISeverity(str, Enum):
    NONE = "NONE"
    SENSITIVE = "SENSITIVE"    # Phone, Email, UPI
    CRITICAL = "CRITICAL"      # PAN, Aadhaar


class AbuseAlertType(str, Enum):
    BOLA_IDOR = "BOLA_IDOR"
    DATA_SCRAPING = "DATA_SCRAPING"
    BYTE_SPIKE = "BYTE_SPIKE"
    TOKEN_REPLAY = "TOKEN_REPLAY"
    WORKFLOW_VIOLATION = "WORKFLOW_VIOLATION"


class OWASPCategory(str, Enum):
    API1_BOLA = "API1:2023 - Broken Object Level Authorization"
    API2_BROKEN_AUTH = "API2:2023 - Broken Authentication"
    API3_PROPERTY_AUTH = "API3:2023 - Broken Object Property Level Authorization"
    API4_UNRESTRICTED_RESOURCE = "API4:2023 - Unrestricted Resource Consumption"
    API6_BUSINESS_FLOW = "API6:2023 - Unrestricted Access to Sensitive Business Flows"
    API9_IMPROPER_INVENTORY = "API9:2023 - Improper Inventory Management"


class PIIMatch(BaseModel):
    entity_type: str            # "PAN", "AADHAAR", "UPI_VPA", "PHONE", "EMAIL", "BEARER_TOKEN"
    count: int = 1
    sample_masked: str          # e.g., "ABCDE****F" or "9876****1234"
    severity: PIISeverity


class AbuseAlert(BaseModel):
    alert_type: AbuseAlertType
    owasp_category: Optional[OWASPCategory] = None
    severity: str = "HIGH"      # "MEDIUM", "HIGH", "CRITICAL"
    confidence: float = 1.0     # 0.0 - 1.0
    reason: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class TelemetryEvent(BaseModel):
    """
    Standardized payload mirrored asynchronously from API Gateway / Telemetry Interceptor.
    """
    request_id: str
    session_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    method: str
    path: str
    query_params: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    request_body: Optional[Union[str, Dict[str, Any], List[Any]]] = None
    status_code: int = 200
    response_headers: Dict[str, str] = Field(default_factory=dict)
    response_body: Optional[Union[str, Dict[str, Any], List[Any]]] = None
    response_size_bytes: int = 0
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    jwt_claims: Optional[Dict[str, Any]] = None
    jwt_sub: Optional[str] = None
    jwt_jti: Optional[str] = None
    ground_truth: Optional[str] = None  # Populated from X-Truth: "benign", "attack_bola", etc.


class ReasonFactor(BaseModel):
    factor: str                 # "Exposure", "PII", "SpecDrift", "AbuseAnomaly", "WorkflowGraph"
    points: int                 # Points contributed to 0-100 score
    description: str            # e.g., "+35 Unauthenticated access"
    owasp_category: Optional[OWASPCategory] = None


class RiskScore(BaseModel):
    """
    Composite explainable risk scoring profile (0-100) per CC6-IC07 specifications.
    """
    request_id: str
    risk_score: int             # 0 to 100
    severity: str               # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    primary_owasp_category: Optional[OWASPCategory] = None
    reason_vector: List[str]    # [ "+35 Unauth", "+25 PII", "+20 Shadow" ]
    factors: List[ReasonFactor]
    parameterized_path: str
    extracted_params: Dict[str, str] = Field(default_factory=dict)
    spec_status: SpecDriftStatus
    pii_matches: List[PIIMatch] = Field(default_factory=list)
    abuse_alerts: List[AbuseAlert] = Field(default_factory=list)
    session_graph: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)
    evaluation_label: Optional[str] = None  # "TP", "FP", "TN", "FN"
