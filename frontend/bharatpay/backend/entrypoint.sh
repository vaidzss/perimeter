#!/bin/sh
set -e

echo "[BharatPay Container] Preparing database directory and tables..."
mkdir -p /data /var/log/bharatpay

python -c "
import sys
sys.path.insert(0, '/app')
from app.db.base import Base
from app.db.session import engine
import app.models
Base.metadata.create_all(bind=engine)
print('[BharatPay Container] Database schema ready.')
"

# Seed data if users table is empty
python -c "
import sys
sys.path.insert(0, '/app')
from app.db.session import SessionLocal
from app.models.user import User
db = SessionLocal()
count = db.query(User).count()
db.close()
if count < 18:
    print('[BharatPay Container] Seeding initial 18 accounts and merchants...')
    from seed import seed_database
    seed_database()
else:
    print('[BharatPay Container] Database already populated.')
"

echo "[BharatPay Container] Starting Uvicorn API server on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
