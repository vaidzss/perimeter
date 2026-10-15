"""
Core Discovery, Abuse Detection & Risk Engine Pipeline.
Orchestrates Box A (Discovery), Box B (Runtime Abuse), Box C (Explainable Scoring),
Context-Aware Session Graphing, and State/Persistence with < 0.5ms latency overhead.
"""

import time
import os
from typing import Tuple, Dict, Any, Optional, List

from core.models import (
    TelemetryEvent,
    RiskScore,
    AbuseAlert,
    SpecDriftStatus,
    PIISeverity
)
from core.discovery.parameterizer import URLParameterizer
from core.discovery.pii_classifier import PIIClassifier
from core.discovery.spec_comparator import OpenAPISpecComparator
from core.abuse.baseline import BaselineProfiler
from core.abuse.bola_detector import BOLADetector
from core.abuse.scraping_detector import ScrapingDetector
from core.abuse.replay_detector import TokenReplayDetector
from core.graph.session_graph import SessionGraphEngine
from core.scoring.risk_scorer import RiskScorer
from storage.state_store import StateStore
from storage.telemetry_db import TelemetryDB


class CoreDetectionEngine:
    """
    Main engine unifying Box A, Box B, Box C, Session Graphing and Telemetry Persistence.
    """

    def __init__(self, openapi_spec_path: Optional[str] = None, db_path: str = "telemetry.db"):
        # Storage
        self.state_store = StateStore()
        self.telemetry_db = TelemetryDB(db_path=db_path)

        # Box A: Discovery & Shadow Diff
        self.parameterizer = URLParameterizer()
        self.pii_classifier = PIIClassifier()
        self.spec_comparator = OpenAPISpecComparator()
        
        if openapi_spec_path and os.path.exists(openapi_spec_path):
            self.spec_comparator.load_spec_from_file(openapi_spec_path)

        # Box B: Runtime Abuse Detection
        self.baseline_profiler = BaselineProfiler()
        self.bola_detector = BOLADetector(window_seconds=60.0, unique_id_threshold=5)
        self.scraping_detector = ScrapingDetector(self.baseline_profiler, window_seconds=60.0)
        self.replay_detector = TokenReplayDetector(window_seconds=60.0)

        # Context-Aware Session Graphing Engine
        self.session_graph_engine = SessionGraphEngine(session_ttl=300.0)

        # Box C: Explainable Risk Scorer
        self.risk_scorer = RiskScorer()

    def process_telemetry(self, event: TelemetryEvent) -> Tuple[RiskScore, float]:
        """
        Executes full Layer 2 inspection on a mirrored telemetry event.
        Returns: (RiskScore, execution_latency_ms)
        """
        t_start = time.perf_counter()

        # -------------------------------------------------------------
        # Box A: Discovery & Shadow Diff
        # -------------------------------------------------------------
        # 1. Parameterize URL
        parameterized_path, extracted_params = self.parameterizer.parameterize(event.path)

        # 2. Classify PII in response body (and request body if present)
        pii_matches, pii_severity = self.pii_classifier.classify_payload(event.response_body)
        if event.request_body and pii_severity != PIISeverity.CRITICAL:
            req_matches, req_sev = self.pii_classifier.classify_payload(event.request_body)
            if req_sev == PIISeverity.CRITICAL or (req_sev == PIISeverity.SENSITIVE and pii_severity == PIISeverity.NONE):
                pii_matches.extend(req_matches)
                pii_severity = req_sev

        # 3. OpenAPI 3.0 Spec Comparison
        spec_status, matched_template, _ = self.spec_comparator.compare(event.method, event.path)

        # -------------------------------------------------------------
        # Box B: Runtime Abuse Detection & Session Graphing
        # -------------------------------------------------------------
        abuse_alerts: List[AbuseAlert] = []
        route_key = f"{event.method.upper()}:{parameterized_path}"
        client_key = event.jwt_sub or event.client_ip or "anonymous"
        session_key = event.session_id or event.jwt_sub or event.client_ip or "anonymous_session"

        # 1. BOLA / IDOR Sequence Check (OWASP API1:2023)
        bola_alert = self.bola_detector.inspect(
            jwt_sub=event.jwt_sub,
            extracted_params=extracted_params,
            route=parameterized_path,
            timestamp=event.timestamp
        )
        if bola_alert:
            abuse_alerts.append(bola_alert)

        # 2. Data Scraping & Harvesting Check (OWASP API4:2023)
        scraping_alert = self.scraping_detector.inspect(
            client_id=client_key,
            route_key=route_key,
            response_bytes=event.response_size_bytes,
            timestamp=event.timestamp
        )
        if scraping_alert:
            abuse_alerts.append(scraping_alert)

        # 3. Token Misuse & Replay Check (OWASP API2:2023)
        replay_alert = self.replay_detector.inspect(
            jwt_jti=event.jwt_jti,
            jwt_sub=event.jwt_sub,
            client_ip=event.client_ip,
            user_agent=event.user_agent,
            timestamp=event.timestamp
        )
        if replay_alert:
            abuse_alerts.append(replay_alert)

        # 4. Context-Aware Session Graph Analysis (OWASP API6:2023)
        workflow_alert, session_graph_data = self.session_graph_engine.record_transition(
            session_id=session_key,
            route_key=route_key,
            timestamp=event.timestamp
        )
        if workflow_alert:
            abuse_alerts.append(workflow_alert)

        # -------------------------------------------------------------
        # Box C: Explainable Risk Scorer (0-100)
        # -------------------------------------------------------------
        risk_score = self.risk_scorer.calculate_score(
            event=event,
            parameterized_path=parameterized_path,
            extracted_params=extracted_params,
            spec_status=spec_status,
            pii_matches=pii_matches,
            pii_severity=pii_severity,
            abuse_alerts=abuse_alerts,
            session_graph=session_graph_data
        )

        # -------------------------------------------------------------
        # Persistence & Audit Log
        # -------------------------------------------------------------
        self.telemetry_db.record_event(event, risk_score)

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        return risk_score, t_elapsed_ms

    def get_inventory(self) -> List[Dict[str, Any]]:
        return self.telemetry_db.get_inventory()

    def get_recent_alerts(self, min_score: int = 60, limit: int = 50) -> List[Dict[str, Any]]:
        return self.telemetry_db.get_recent_alerts(min_score=min_score, limit=limit)

    def get_confusion_matrix(self) -> Dict[str, Any]:
        return self.telemetry_db.get_confusion_matrix()

    def get_session_graph(self, session_id: str) -> Dict[str, Any]:
        return self.session_graph_engine.export_session_graph(session_id)
