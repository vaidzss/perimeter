from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.base import Base

class RequestLog(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(36), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    method = Column(String(10), nullable=False)
    raw_path = Column(Text, nullable=False)
    path_template = Column(String(255), index=True, nullable=False)
    query_params = Column(Text, default="[]", nullable=False)
    status_code = Column(Integer, index=True, nullable=False)
    response_size = Column(Integer, default=0, nullable=False)
    request_size = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    client_ip = Column(String(45), index=True, nullable=False)
    user_agent = Column(Text, nullable=True)
    auth_type = Column(String(20), default="none", nullable=False)
    token_id = Column(String(64), index=True, nullable=True)
    user_id = Column(String(32), index=True, nullable=True)
    object_ids = Column(Text, default="[]", nullable=False)  # JSON encoded list
    sensitive_types = Column(Text, default="[]", nullable=False)  # JSON encoded list
