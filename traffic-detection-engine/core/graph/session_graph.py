"""
Context-Aware Session Graphing Engine.
Constructs stateful Directed Behavioral Graphs (DAGs) per session.
Detects:
1. Out-of-Order / Skip-Step Workflow Violations (OWASP API6:2023)
2. High-Entropy Random-Walk Reconnaissance & Route Fuzzing
3. Exports Graph Topology (Nodes & Edges) for SOC Command Center Visualization
"""

import time
import math
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any, Set
from core.models import AbuseAlert, AbuseAlertType, OWASPCategory


class SessionGraphEngine:
    """
    Maintains per-session directed behavioral graphs and baseline transition matrices.
    """

    def __init__(self, session_ttl: float = 300.0, max_sessions: int = 10000):
        self.session_ttl = session_ttl
        self.max_sessions = max_sessions

        # Key: session_id -> {
        #   "last_seen": float,
        #   "current_node": Optional[str],
        #   "nodes": Dict[str, int],  # endpoint -> visit count
        #   "edges": Dict[Tuple[str, str], int],  # (src, dst) -> count
        #   "history": Deque[str]
        # }
        self.sessions: Dict[str, Dict[str, Any]] = {}

        # Global learned transition counts: (src, dst) -> count
        self.transition_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self.src_totals: Dict[str, int] = defaultdict(int)

        # Baseline sensitive endpoints requiring prerequisite flow
        self.sensitive_sinks: Set[str] = {
            "POST:/api/v2/payments/transfer",
            "POST:/api/internal/debug/reset",
            "GET:/api/v1/users/export-all"
        }

        # Known valid entry/anchor endpoints
        self.valid_anchors: Set[str] = {
            "GET:/api/v2/accounts/{id}/balance",
            "GET:/api/v2/users/{id}/profile",
            "GET:/api/v2/users/me",
            "PUT:/api/v2/users/me/contact",
            "GET:/api/v2/auth/me",
            "GET:/api/v2/accounts/{account_id}",
            "GET:/api/v2/accounts/{account_id}/statements",
            "GET:/api/v2/accounts/{account_id}/transactions",
            "POST:/api/v2/accounts/beneficiaries",
            "GET:/api/v2/transactions/{id}/receipt",
            "GET:/api/v2/transactions/{txn_id}/receipt",
            "POST:/api/v2/payments/upi-transfer",
            "POST:/api/v2/auth/login"
        }

    def _cleanup_expired(self, now: float):
        cutoff = now - self.session_ttl
        expired = [sid for sid, data in self.sessions.items() if data["last_seen"] < cutoff]
        for sid in expired:
            del self.sessions[sid]

    def record_transition(self,
                          session_id: str,
                          route_key: str,
                          timestamp: Optional[float] = None) -> Tuple[Optional[AbuseAlert], Dict[str, Any]]:
        """
        Records an endpoint visit within the session graph, updates transition matrices,
        and evaluates workflow validity.
        Returns: (Optional[AbuseAlert], graph_summary)
        """
        now = timestamp if timestamp is not None else time.time()
        self._cleanup_expired(now)

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "last_seen": now,
                "current_node": None,
                "nodes": defaultdict(int),
                "edges": defaultdict(int),
                "history": deque(maxlen=30)
            }

        session = self.sessions[session_id]
        session["last_seen"] = now
        prev_node = session["current_node"]

        # Update session nodes and history
        session["nodes"][route_key] += 1
        session["history"].append(route_key)
        session["current_node"] = route_key

        # Update edge if transition occurred
        if prev_node:
            transition = (prev_node, route_key)
            session["edges"][transition] += 1
            self.transition_counts[transition] += 1
            self.src_totals[prev_node] += 1

        # -------------------------------------------------------------
        # Anomaly Check 1: Sensitive Business Flow Bypass (Skip-step)
        # -------------------------------------------------------------
        # If invoking a sensitive sink without any prior anchor in session
        alert: Optional[AbuseAlert] = None
        has_anchor = any(anchor in session["nodes"] for anchor in self.valid_anchors)

        if route_key in self.sensitive_sinks and not has_anchor:
            alert = AbuseAlert(
                alert_type=AbuseAlertType.WORKFLOW_VIOLATION,
                owasp_category=OWASPCategory.API6_BUSINESS_FLOW,
                severity="CRITICAL",
                confidence=0.95,
                reason=f"Sensitive workflow '{route_key}' invoked directly without preceding authentication or profile workflow",
                details={
                    "session_id": session_id,
                    "target_sink": route_key,
                    "session_steps": len(session["history"]),
                    "history": list(session["history"]),
                    "missing_prerequisites": list(self.valid_anchors)
                },
                timestamp=now
            )

        # -------------------------------------------------------------
        # Anomaly Check 2: High Branching Entropy (Reconnaissance Scanner)
        # -------------------------------------------------------------
        unique_nodes_count = len(session["nodes"])
        total_steps = len(session["history"])

        # If a session accesses >= 7 unique endpoints with zero repeat transitions (broad scanner sweep)
        # Exclude legitimate authentication login and anchor endpoints
        is_anchor_or_auth = route_key in self.valid_anchors or any(a in route_key.lower() for a in ("/auth/login", "/auth/"))
        if total_steps >= 7 and unique_nodes_count >= 6 and not alert and not is_anchor_or_auth:
            # Calculate node entropy
            probs = [count / total_steps for count in session["nodes"].values()]
            entropy = -sum(p * math.log2(p) for p in probs)
            max_entropy = math.log2(unique_nodes_count)
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 1.0

            if normalized_entropy > 0.92:
                alert = AbuseAlert(
                    alert_type=AbuseAlertType.WORKFLOW_VIOLATION,
                    owasp_category=OWASPCategory.API6_BUSINESS_FLOW,
                    severity="HIGH",
                    confidence=0.90,
                    reason=f"Anomalous high-entropy API graph traversal (H={normalized_entropy:.2f}): rapid random-walk reconnaissance across {unique_nodes_count} distinct endpoints",
                    details={
                        "session_id": session_id,
                        "unique_endpoints": unique_nodes_count,
                        "total_steps": total_steps,
                        "normalized_entropy": round(normalized_entropy, 3),
                        "endpoints_visited": list(session["nodes"].keys())
                    },
                    timestamp=now
                )

        # Build Graph Representation for SOC Dashboard
        graph_data = self.export_session_graph(session_id)
        return alert, graph_data

    def export_session_graph(self, session_id: str) -> Dict[str, Any]:
        """
        Exports the Cytoscape / D3 graph nodes & edges representation for the session.
        """
        if session_id not in self.sessions:
            return {"session_id": session_id, "nodes": [], "edges": [], "total_steps": 0}

        s = self.sessions[session_id]
        nodes = [
            {"id": ep, "label": ep.split(":")[-1], "method": ep.split(":")[0], "count": count}
            for ep, count in s["nodes"].items()
        ]

        edges = [
            {"source": src, "target": dst, "weight": count}
            for (src, dst), count in s["edges"].items()
        ]

        return {
            "session_id": session_id,
            "nodes": nodes,
            "edges": edges,
            "total_steps": len(s["history"]),
            "current_node": s["current_node"]
        }
