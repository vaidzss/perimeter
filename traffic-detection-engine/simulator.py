"""
Standalone Poisson Process Threat Simulator.
Generates synthetic, mathematically grounded traffic with Poisson arrival intervals
(Δt ~ Exp(λ)) and multi-vector threat patterns mapped directly to OWASP API Top 10 (2023).

Usage:
    python simulator.py --mode=direct --events=150 --rate=20
    python simulator.py --mode=http --target-url=http://localhost:8000/api/telemetry --events=100
"""

import sys
import os
import time
import random
import argparse
import json
from typing import Generator, Dict, Any, List

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import TelemetryEvent
from pipeline import CoreDetectionEngine


class PoissonTrafficSimulator:
    """
    Simulates realistic human and attack API traffic using Poisson processes.
    """

    def __init__(self, target_lambda: float = 15.0):
        """
        target_lambda: average requests per second (λ)
        """
        self.lambd = target_lambda
        self.benign_users = [f"usr_{1000 + i}" for i in range(12)]

    def generate_inter_arrival_delay(self) -> float:
        """
        Generates inter-arrival time according to Poisson process: Δt = -ln(1 - U) / λ
        """
        return random.expovariate(self.lambd)

    def generate_benign_event(self, req_id: str, timestamp: float) -> TelemetryEvent:
        user = random.choice(self.benign_users)
        account_id = user.replace("usr_", "acc_")
        session_id = f"sess_{user}"

        # Natural workflow steps
        step = random.choices(["profile", "balance", "transfer"], weights=[0.4, 0.5, 0.1])[0]

        if step == "profile":
            path = f"/api/v2/users/{user}/profile"
            method = "GET"
            body = {"user_id": user, "status": "ACTIVE"}
            size = 52
        elif step == "balance":
            path = f"/api/v2/accounts/{account_id}/balance"
            method = "GET"
            body = {"account_id": account_id, "balance": random.randint(10000, 500000)}
            size = 48
        else:
            path = "/api/v2/payments/transfer"
            method = "POST"
            body = {"tx_id": f"TXN-{random.randint(10000, 99999)}", "status": "COMPLETED"}
            size = 65

        return TelemetryEvent(
            request_id=req_id,
            session_id=session_id,
            timestamp=timestamp,
            method=method,
            path=path,
            headers={
                "authorization": f"Bearer valid.jwt.{user}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
                "x-forwarded-for": f"192.168.1.{int(user.replace('usr_', '')) % 250}",
                "x-truth": "benign"
            },
            response_body=body,
            response_size_bytes=size,
            client_ip=f"192.168.1.{int(user.replace('usr_', '')) % 250}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            jwt_sub=user,
            jwt_jti=f"jti-{user}",
            ground_truth="benign"
        )

    def generate_bola_attack_event(self, req_id: str, target_id: int, timestamp: float) -> TelemetryEvent:
        return TelemetryEvent(
            request_id=req_id,
            session_id="sess_attacker_bola",
            timestamp=timestamp,
            method="GET",
            path=f"/api/v2/accounts/{target_id}/balance",
            headers={
                "authorization": "Bearer valid.jwt.attacker",
                "user-agent": "Python-requests/2.31",
                "x-forwarded-for": "198.51.100.44",
                "x-truth": "attack_bola"
            },
            response_body={"account_id": str(target_id), "balance": random.randint(1000, 900000)},
            response_size_bytes=50,
            client_ip="198.51.100.44",
            user_agent="Python-requests/2.31",
            jwt_sub="usr_attacker_99",
            jwt_jti="jti-attacker-99",
            ground_truth="attack_bola"
        )

    def generate_scraping_event(self, req_id: str, target_id: int, timestamp: float) -> TelemetryEvent:
        return TelemetryEvent(
            request_id=req_id,
            session_id="sess_bot_scraper",
            timestamp=timestamp,
            method="GET",
            path=f"/api/v2/users/{target_id}/profile",
            headers={
                "authorization": "Bearer valid.jwt.scraper",
                "user-agent": "Scrapy/2.11 Bot",
                "x-forwarded-for": "203.0.113.88",
                "x-truth": "attack_scraping"
            },
            response_body={"user_id": str(target_id), "name": f"User {target_id}"},
            response_size_bytes=60,
            client_ip="203.0.113.88",
            user_agent="Scrapy/2.11 Bot",
            jwt_sub="usr_bot_scraper",
            jwt_jti="jti-bot-scraper",
            ground_truth="attack_scraping"
        )

    def generate_replay_event(self, req_id: str, ip: str, ua: str, timestamp: float) -> TelemetryEvent:
        return TelemetryEvent(
            request_id=req_id,
            session_id="sess_replay_hijack",
            timestamp=timestamp,
            method="GET",
            path="/api/v2/accounts/9841/balance",
            headers={
                "authorization": "Bearer stolen.jwt.token",
                "user-agent": ua,
                "x-forwarded-for": ip,
                "x-truth": "attack_replay"
            },
            response_body={"account_id": "9841", "balance": 150000},
            response_size_bytes=45,
            client_ip=ip,
            user_agent=ua,
            jwt_sub="usr_victim",
            jwt_jti="jti-stolen-token-unique",
            ground_truth="attack_replay"
        )

    def generate_workflow_violation_event(self, req_id: str, timestamp: float) -> TelemetryEvent:
        """Invoking financial transfer out-of-order with zero prior session history."""
        return TelemetryEvent(
            request_id=req_id,
            session_id=f"sess_skip_step_{random.randint(1000, 9999)}",
            timestamp=timestamp,
            method="POST",
            path="/api/v2/payments/transfer",
            headers={
                "authorization": "Bearer token.unlinked",
                "user-agent": "curl/8.4.0",
                "x-forwarded-for": "185.220.101.5",
                "x-truth": "attack_workflow"
            },
            response_body={"tx_id": "TXN-99999", "status": "COMPLETED"},
            response_size_bytes=65,
            client_ip="185.220.101.5",
            user_agent="curl/8.4.0",
            jwt_sub="usr_stealth_attacker",
            jwt_jti=f"jti-skip-{random.randint(100, 999)}",
            ground_truth="attack_workflow"
        )

    def generate_shadow_event(self, req_id: str, timestamp: float) -> TelemetryEvent:
        return TelemetryEvent(
            request_id=req_id,
            session_id="sess_recon_shadow",
            timestamp=timestamp,
            method="POST",
            path="/api/internal/debug/reset",
            headers={"x-truth": "attack_shadow"},
            response_body={"debug": "state reset executed"},
            response_size_bytes=35,
            client_ip="192.168.1.200",
            ground_truth="attack_shadow"
        )

    def generate_zombie_event(self, req_id: str, timestamp: float) -> TelemetryEvent:
        return TelemetryEvent(
            request_id=req_id,
            session_id="sess_legacy_zombie",
            timestamp=timestamp,
            method="GET",
            path="/api/v1/users/export-all",
            headers={"authorization": "Bearer valid.jwt", "x-truth": "attack_zombie"},
            response_body={"export": [{"pan": "ABCDE1234F", "aadhaar": "284759283713"}]},
            response_size_bytes=8500,
            client_ip="10.0.0.99",
            ground_truth="attack_zombie"
        )

    def stream_traffic(self, total_events: int = 150) -> Generator[TelemetryEvent, None, None]:
        sim_time = time.time()
        bola_counter = 5000
        scraping_counter = 2000

        for i in range(total_events):
            sim_time += self.generate_inter_arrival_delay()
            req_id = f"sim-req-{i:04d}"

            # Traffic mixture: 60% Benign, 40% Multi-Vector Attacks
            scenario = random.choices(
                ["benign", "bola", "scraping", "replay", "workflow", "shadow", "zombie"],
                weights=[0.55, 0.12, 0.10, 0.08, 0.05, 0.05, 0.05]
            )[0]

            if scenario == "benign":
                yield self.generate_benign_event(req_id, sim_time)
            elif scenario == "bola":
                bola_counter += 1
                yield self.generate_bola_attack_event(req_id, bola_counter, sim_time)
            elif scenario == "scraping":
                scraping_counter += 1
                yield self.generate_scraping_event(req_id, scraping_counter, sim_time)
            elif scenario == "replay":
                ip = f"185.220.101.{random.randint(1, 10)}"
                ua = f"Browser-{random.randint(1, 4)}"
                yield self.generate_replay_event(req_id, ip, ua, sim_time)
            elif scenario == "workflow":
                yield self.generate_workflow_violation_event(req_id, sim_time)
            elif scenario == "shadow":
                yield self.generate_shadow_event(req_id, sim_time)
            elif scenario == "zombie":
                yield self.generate_zombie_event(req_id, sim_time)


def run_direct_simulation(events: int, rate: float):
    print("=" * 70)
    print("[SIMULATOR] RUNNING STANDALONE POISSON THREAT SIMULATOR (Direct Pipeline Mode)")
    print(f"  * Event Count: {events}")
    print(f"  * Poisson Arrival Rate (lambda): {rate} req/sec")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(base_dir, "config", "openapi.json")
    engine = CoreDetectionEngine(openapi_spec_path=spec_path, db_path=":memory:")
    simulator = PoissonTrafficSimulator(target_lambda=rate)

    latencies = []
    processed = 0

    t_start = time.perf_counter()
    for event in simulator.stream_traffic(total_events=events):
        score, latency_ms = engine.process_telemetry(event)
        latencies.append(latency_ms)
        processed += 1

    t_total = time.perf_counter() - t_start
    avg_latency = sum(latencies) / len(latencies)
    cm = engine.get_confusion_matrix()

    print("\n" + "=" * 70)
    print("[METRICS] SIMULATION BENCHMARK & EVALUATION RESULTS")
    print("=" * 70)
    print(f"  * Total Processed:          {processed} events in {t_total:.3f}s")
    print(f"  * Average Ingestion Latency: {avg_latency:.3f} ms / request")
    print(f"  * Peak Engine Throughput:    {int(1000.0 / avg_latency if avg_latency > 0 else 0):,} req/sec")
    print("-" * 70)
    print(f"  * True Positives (TP):      {cm['tp']}")
    print(f"  * False Positives (FP):     {cm['fp']}")
    print(f"  * True Negatives (TN):      {cm['tn']}")
    print(f"  * False Negatives (FN):     {cm['fn']}")
    print(f"  * True Positive Rate (TPR): {cm['tpr_percentage']}%")
    print(f"  * False Positive Rate (FPR): {cm['fpr_percentage']}%")
    print("=" * 70)


def run_http_simulation(events: int, rate: float, target_url: str):
    import requests
    print("=" * 70)
    print("[SIMULATOR] STREAMING POISSON TRAFFIC VIA HTTP TO ENGINE")
    print(f"  * Target Endpoint: {target_url}")
    print(f"  * Event Count:     {events}")
    print(f"  * Poisson Rate:    {rate} req/sec")
    print("=" * 70)

    simulator = PoissonTrafficSimulator(target_lambda=rate)
    sent = 0
    for event in simulator.stream_traffic(total_events=events):
        delay = simulator.generate_inter_arrival_delay()
        time.sleep(min(delay, 0.05))  # Smooth throttle
        try:
            resp = requests.post(target_url, json=event.model_dump(), timeout=2.0)
            data = resp.json()
            sent += 1
            if sent % 10 == 0 or data.get("severity") in ("HIGH", "CRITICAL"):
                print(f"[{sent:03d}/{events}] {event.method} {event.path} -> Score: {data.get('risk_score')}/100 [{data.get('severity')}] {data.get('reason_vector')}")
        except Exception as e:
            print(f"HTTP Post Error: {e}")
            break

    print(f"\n[DONE] Completed streaming {sent} events to {target_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poisson Process API Threat Simulator")
    parser.add_argument("--mode", choices=["direct", "http"], default="direct", help="Simulation mode")
    parser.add_argument("--events", type=int, default=150, help="Number of telemetry events to simulate")
    parser.add_argument("--rate", type=float, default=20.0, help="Poisson arrival rate lambda (req/sec)")
    parser.add_argument("--target-url", type=str, default="http://localhost:8000/api/telemetry", help="Target API URL for http mode")
    args = parser.parse_args()

    if args.mode == "direct":
        run_direct_simulation(events=args.events, rate=args.rate)
    else:
        run_http_simulation(events=args.events, rate=args.rate, target_url=args.target_url)
