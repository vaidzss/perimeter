"""
Telemetry Database & API Inventory Store.
Persists discovered endpoints, shadow/zombie classifications, forensic request logs,
and calculates the live Confusion Matrix (TPR, FPR, TP, FP, TN, FN).
"""

import sqlite3
import json
import time
import threading
from typing import Dict, List, Any, Optional
from core.models import RiskScore, TelemetryEvent


class TelemetryDB:
    """
    SQLite persistence layer for telemetry storage and evaluation analytics.
    """

    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
        else:
            self._persistent_conn = None
        self._init_db()

    def _get_connection(self):
        if self._persistent_conn is not None:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # API Inventory Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_inventory (
                    route_key TEXT PRIMARY KEY,
                    method TEXT,
                    parameterized_path TEXT,
                    spec_status TEXT,
                    pii_types TEXT,
                    first_seen REAL,
                    last_seen REAL,
                    request_count INTEGER DEFAULT 1,
                    max_risk_score INTEGER DEFAULT 0
                )
            """)

            # Forensic Audit Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forensic_logs (
                    request_id TEXT PRIMARY KEY,
                    timestamp REAL,
                    method TEXT,
                    raw_path TEXT,
                    parameterized_path TEXT,
                    status_code INTEGER,
                    risk_score INTEGER,
                    severity TEXT,
                    reason_vector TEXT,
                    client_ip TEXT,
                    user_agent TEXT,
                    jwt_sub TEXT,
                    ground_truth TEXT,
                    eval_label TEXT
                )
            """)

            # Confusion Matrix / Evaluation Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eval_metrics (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    tp INTEGER DEFAULT 0,
                    fp INTEGER DEFAULT 0,
                    tn INTEGER DEFAULT 0,
                    fn INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO eval_metrics (id, tp, fp, tn, fn, total) VALUES (1, 0, 0, 0, 0, 0)")
            conn.commit()

    def record_event(self, event: TelemetryEvent, risk: RiskScore):
        route_key = f"{event.method.upper()}:{risk.parameterized_path}"
        pii_str = ",".join(set(m.entity_type for m in risk.pii_matches))
        now = event.timestamp

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Upsert into Inventory
            cursor.execute("""
                INSERT INTO api_inventory (
                    route_key, method, parameterized_path, spec_status, pii_types, 
                    first_seen, last_seen, request_count, max_risk_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(route_key) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    request_count = api_inventory.request_count + 1,
                    max_risk_score = MAX(api_inventory.max_risk_score, excluded.max_risk_score),
                    spec_status = excluded.spec_status,
                    pii_types = CASE 
                        WHEN api_inventory.pii_types = '' THEN excluded.pii_types 
                        WHEN excluded.pii_types = '' THEN api_inventory.pii_types
                        ELSE api_inventory.pii_types || ',' || excluded.pii_types 
                    END
            """, (
                route_key, event.method.upper(), risk.parameterized_path,
                risk.spec_status.value, pii_str, now, now, risk.risk_score
            ))

            # Insert Forensic Log
            reason_json = json.dumps(risk.reason_vector)
            cursor.execute("""
                INSERT OR REPLACE INTO forensic_logs (
                    request_id, timestamp, method, raw_path, parameterized_path,
                    status_code, risk_score, severity, reason_vector,
                    client_ip, user_agent, jwt_sub, ground_truth, eval_label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.request_id, now, event.method.upper(), event.path,
                risk.parameterized_path, event.status_code, risk.risk_score,
                risk.severity, reason_json, event.client_ip or "",
                event.user_agent or "", event.jwt_sub or "",
                event.ground_truth or "", risk.evaluation_label or ""
            ))

            # Update Confusion Matrix counters if ground truth was provided
            if risk.evaluation_label:
                lbl = risk.evaluation_label
                tp_inc = 1 if lbl == "TP" else 0
                fp_inc = 1 if lbl == "FP" else 0
                tn_inc = 1 if lbl == "TN" else 0
                fn_inc = 1 if lbl == "FN" else 0

                cursor.execute("""
                    UPDATE eval_metrics SET
                        tp = tp + ?,
                        fp = fp + ?,
                        tn = tn + ?,
                        fn = fn + ?,
                        total = total + 1
                    WHERE id = 1
                """, (tp_inc, fp_inc, tn_inc, fn_inc))

            conn.commit()

    def get_inventory(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM api_inventory ORDER BY last_seen DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_recent_alerts(self, min_score: int = 60, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM forensic_logs 
                WHERE risk_score >= ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (min_score, limit))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["reason_vector"] = json.loads(item["reason_vector"]) if item["reason_vector"] else []
                results.append(item)
            return results

    def get_confusion_matrix(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tp, fp, tn, fn, total FROM eval_metrics WHERE id = 1")
            row = cursor.fetchone()
            if not row:
                return {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "total": 0, "tpr": 0.0, "fpr": 0.0}

            tp, fp, tn, fn, total = row["tp"], row["fp"], row["tn"], row["fn"], row["total"]
            
            # TPR = TP / (TP + FN)
            tpr = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
            # FPR = FP / (FP + TN)
            fpr = (fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0

            return {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "total_evaluated": total,
                "tpr_percentage": round(tpr, 2),
                "fpr_percentage": round(fpr, 2)
            }
