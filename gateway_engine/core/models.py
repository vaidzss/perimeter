"""
SQLAlchemy Async ORM Models for SentinelAPI.
Defines persistent entities: DiscoveredAPI, SecurityAlert, and ForensicRequestLog.
"""

import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, Text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DiscoveredAPI(Base):
    __tablename__ = "discovered_apis"

    id = Column(String(128), primary_key=True, index=True)
    method = Column(String(16), nullable=False, index=True)
    path = Column(String(512), nullable=False)
    normalized_path = Column(String(512), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="DOCUMENTED", index=True)  # DOCUMENTED, SHADOW, ZOMBIE
    service = Column(String(128), default="fintech-core")
    host = Column(String(128), default="api.fintech.mesh")
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(32), default="low")  # critical, high, medium, low
    auth_type = Column(String(64), default="None")  # JWT Bearer, Weak Auth, None
    pii_detected = Column(JSON, default=list)        # ['PAN_CARD', 'UPI_VPA', ...]
    rps = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    spec_drift = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    active_threat_count = Column(Integer, default=0)
    risk_reasons = Column(JSON, default=list)       # Explainable reasons list
    auto_swagger_spec = Column(JSON, default=dict)  # Auto-generated OpenAPI snippet for shadow APIs
    quarantined = Column(Boolean, default=False)
    mask_pii = Column(Boolean, default=False)
    honeypot_bola = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "method": self.method,
            "path": self.path,
            "normalized_path": self.normalized_path,
            "status": self.status,
            "service": self.service,
            "host": self.host,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "auth_type": self.auth_type,
            "pii_detected": self.pii_detected or [],
            "rps": self.rps,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "spec_drift": self.spec_drift,
            "tags": self.tags or [],
            "active_threat_count": self.active_threat_count,
            "risk_reasons": self.risk_reasons or [],
            "auto_swagger_spec": self.auto_swagger_spec or {},
            "quarantined": self.quarantined,
            "mask_pii": self.mask_pii,
            "honeypot_bola": self.honeypot_bola
        }


class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    severity = Column(String(32), nullable=False, index=True)  # critical, high, medium, low
    category = Column(String(64), nullable=False, index=True)  # BOLA / IDOR, Data Scraping, etc.
    threat_actor_ip = Column(String(64), nullable=False, index=True)
    endpoint = Column(String(512), nullable=False)
    method = Column(String(16), nullable=False)
    status = Column(String(32), default="active", index=True)  # active, investigating, mitigated
    description = Column(Text, nullable=False)
    owasp_category = Column(String(128), default="API1:2023 - Broken Object Level Authorization")
    forensic_data = Column(JSON, default=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "severity": self.severity,
            "category": self.category,
            "threat_actor_ip": self.threat_actor_ip,
            "endpoint": self.endpoint,
            "method": self.method,
            "status": self.status,
            "description": self.description,
            "owasp_category": self.owasp_category,
            "forensic_data": self.forensic_data or {}
        }


class ForensicRequestLog(Base):
    __tablename__ = "forensic_request_logs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    client_ip = Column(String(64), nullable=False, index=True)
    user_agent = Column(String(256), default="")
    method = Column(String(16), nullable=False)
    path = Column(String(512), nullable=False)
    normalized_path = Column(String(512), nullable=False, index=True)
    query_params = Column(String(512), default="")
    request_headers = Column(JSON, default=dict)
    response_status = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    jwt_sub = Column(String(128), nullable=True, index=True)
    jwt_jti = Column(String(128), nullable=True)
    x_truth = Column(String(64), nullable=True)  # Ground-truth: benign, attack_bola, etc.
    flagged_anomalies = Column(JSON, default=list)
    mitigation_action = Column(String(64), default="NONE")  # NONE, QUARANTINED, PII_MASKED, BLOCKED
    response_body_sample = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "method": self.method,
            "path": self.path,
            "normalized_path": self.normalized_path,
            "query_params": self.query_params,
            "request_headers": self.request_headers or {},
            "response_status": self.response_status,
            "latency_ms": self.latency_ms,
            "jwt_sub": self.jwt_sub,
            "jwt_jti": self.jwt_jti,
            "x_truth": self.x_truth,
            "flagged_anomalies": self.flagged_anomalies or [],
            "mitigation_action": self.mitigation_action,
            "response_body_sample": self.response_body_sample
        }
