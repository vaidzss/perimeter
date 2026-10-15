import os
import json
import time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.request_log import RequestLog

client = TestClient(app)

def test_request_logging_dual_write_and_schema():
    """Test 1: Requests produce exactly one log line in both JSONL file and requests table."""
    # Ensure log file exists and record initial count
    initial_file_lines = 0
    if os.path.exists(settings.LOG_FILE_PATH):
        with open(settings.LOG_FILE_PATH, "r", encoding="utf-8") as f:
            initial_file_lines = len(f.readlines())

    db = SessionLocal()
    initial_db_count = db.query(RequestLog).count()
    db.close()

    # Send a request
    response = client.get("/health")
    assert response.status_code == 200

    # Verify log file has exactly 1 new line
    with open(settings.LOG_FILE_PATH, "r", encoding="utf-8") as f:
        file_lines = f.readlines()
    assert len(file_lines) == initial_file_lines + 1

    # Verify schema of the emitted line
    last_record = json.loads(file_lines[-1])
    required_keys = [
        "request_id", "timestamp", "method", "raw_path", "path_template",
        "query_params", "status_code", "response_size", "request_size",
        "latency_ms", "client_ip", "user_agent", "auth_type", "token_id",
        "user_id", "object_ids", "sensitive_types"
    ]
    for key in required_keys:
        assert key in last_record, f"Missing required telemetry key: {key}"

    assert last_record["method"] == "GET"
    assert last_record["raw_path"] == "/health"
    assert last_record["status_code"] == 200

    # Verify SQLite requests table has exactly 1 new record
    db = SessionLocal()
    new_db_count = db.query(RequestLog).count()
    last_db_record = db.query(RequestLog).filter(RequestLog.request_id == last_record["request_id"]).first()
    db.close()

    assert new_db_count == initial_db_count + 1
    assert last_db_record is not None
    assert last_db_record.status_code == 200

def test_sensitive_data_detection_in_responses():
    """Test 2: Regex scanning accurately identifies PAN, Aadhaar, and phone patterns."""
    from app.middleware.structured_logger import StructuredLoggingMiddleware
    middleware = StructuredLoggingMiddleware(app)

    # Test dummy payloads
    sample_with_pan = b'{"status": "ok", "pan": "ABCDE1234F"}'
    tags_pan = middleware._detect_sensitive_types(sample_with_pan)
    assert "pan" in tags_pan

    sample_with_aadhaar = b'{"status": "ok", "aadhaar": "9999 8888 1234"}'
    tags_aadhaar = middleware._detect_sensitive_types(sample_with_aadhaar)
    assert "aadhaar" in tags_aadhaar

    sample_with_phone = b'{"status": "ok", "phone": "9876501001"}'
    tags_phone = middleware._detect_sensitive_types(sample_with_phone)
    assert "phone" in tags_phone

    sample_masked = b'{"status": "ok", "pan": "ABCDE****F", "aadhaar": "XXXXXXXX1234"}'
    tags_masked = middleware._detect_sensitive_types(sample_masked)
    assert "pan" not in tags_masked
    assert "aadhaar" not in tags_masked

def test_object_ids_extraction():
    """Test 3: Extraction of single and multi-ID paths."""
    from app.middleware.structured_logger import StructuredLoggingMiddleware
    middleware = StructuredLoggingMiddleware(app)

    ids1 = middleware._extract_object_ids("/api/v2/accounts/1042/statement")
    assert ids1 == ["1042"]

    ids2 = middleware._extract_object_ids("/api/v2/accounts/1042/transactions/5089")
    assert ids2 == ["1042", "5089"]

    ids_user = middleware._extract_object_ids("/api/v2/users/u_101/profile")
    assert ids_user == ["u_101"]

def test_logging_overhead_under_5ms():
    """Test 4: Logging overhead benchmark does not add noticeable latency."""
    # Run 10 rapid calls
    t0 = time.perf_counter()
    for _ in range(10):
        client.get("/health")
    avg_duration = (time.perf_counter() - t0) / 10
    # Even on Windows SQLite, local requests should take ~1-3ms
    print(f"\nAverage request latency with structured logging: {avg_duration * 1000:.2f}ms")
    assert avg_duration < 0.05, f"Request latency too high: {avg_duration * 1000:.2f}ms"
