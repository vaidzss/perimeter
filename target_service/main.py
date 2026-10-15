"""
SentinelAPI FinTech/DPI Vulnerable Target Service (Port 8001).
Simulates a modern Indian FinTech / Digital Public Infrastructure microservice with:
1. Documented V2 APIs: Login (JWT), BOLA-vulnerable Account Balance, Merchant Directory
2. Zombie V1 API: Deprecated unauthenticated PII bulk export (/api/v1/users/export-all)
3. Shadow Internal APIs: Hidden debug & unauthenticated configuration dump routes
"""

import os
import uuid
import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jwt

app = FastAPI(
    title="FinTech DPI Core Banking Service",
    description="Simulated FinTech Target Service with BOLA, Zombie PII leaks, and Shadow APIs",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("TARGET_JWT_SECRET", "sentinel-fintech-jwt-secret-key-9841")
JWT_ALGORITHM = "HS256"

# ==============================================================================
# DATA MODELS
# ==============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "user_101"})
    password: str = Field(..., json_schema_extra={"example": "password123"})

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class AccountBalanceResponse(BaseModel):
    account_id: str
    account_number: str
    account_holder: str
    currency: str = "INR"
    available_balance: float
    ledger_balance: float
    account_type: str
    status: str
    branch_ifsc: str
    last_transaction: str

class MerchantItem(BaseModel):
    merchant_id: str
    business_name: str
    category: str
    upi_vpa: str
    city: str
    state: str
    rating: float
    verified: bool

class MerchantDirectoryResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    data: List[MerchantItem]

class PIIUserExport(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone_number: str
    pan_card: str
    upi_vpa: str
    govt_id_reference: str
    annual_income_inr: float
    session_token_sample: str

class DebugResetRequest(BaseModel):
    target: Optional[str] = "all"
    force: Optional[bool] = False

# ==============================================================================
# IN-MEMORY FINTECH MOCK DATABASE
# ==============================================================================

USERS_DB = {
    "user_101": {
        "password": "password123",
        "account_id": "101",
        "name": "Aarav Sharma",
        "role": "retail_user",
        "email": "aarav.sharma@example.com",
        "phone": "+91-9876543210",
        "pan": "ABCDE1234F",
        "upi": "aarav.sharma@okhdfcbank",
        "balance": 245000.50
    },
    "user_102": {
        "password": "password123",
        "account_id": "102",
        "name": "Priya Patel",
        "role": "retail_user",
        "email": "priya.patel@example.com",
        "phone": "+91-9812345678",
        "pan": "BKRPK4829D",
        "upi": "priyapatel@okaxis",
        "balance": 682400.00
    },
    "user_103": {
        "password": "password123",
        "account_id": "103",
        "name": "Rohan Verma",
        "role": "retail_user",
        "email": "rohan.verma@example.com",
        "phone": "+91-9723456789",
        "pan": "CPDPV9182M",
        "upi": "rohan.v@oksbi",
        "balance": 18950.25
    },
    "user_104": {
        "password": "password123",
        "account_id": "104",
        "name": "Ananya Iyer",
        "role": "retail_user",
        "email": "ananya.iyer@example.com",
        "phone": "+91-9654321098",
        "pan": "DFEPI3391K",
        "upi": "ananya.iyer@okicici",
        "balance": 1245000.00
    },
    "admin_999": {
        "password": "adminsecret999",
        "account_id": "999",
        "name": "FinTech Operations Admin",
        "role": "admin",
        "email": "sec-ops@fintech.mesh",
        "phone": "+91-9999988888",
        "pan": "ZZZPK9999Z",
        "upi": "fintechops@okhdfcbank",
        "balance": 99999999.00
    }
}

MERCHANTS_DB = [
    {"merchant_id": f"MERC-{i:03d}",
     "business_name": name,
     "category": cat,
     "upi_vpa": upi,
     "city": city,
     "state": state,
     "rating": rating,
     "verified": True}
    for i, (name, cat, upi, city, state, rating) in enumerate([
        ("Sharma Kirana Store", "GROCERY", "sharmakiran@okhdfcbank", "Mumbai", "Maharashtra", 4.8),
        ("Apollo Pharmacy Partner", "HEALTHCARE", "apollomeds@okaxis", "Bengaluru", "Karnataka", 4.9),
        ("Bikanervala Sweets", "FOOD_BEVERAGE", "bikanervala@oksbi", "New Delhi", "Delhi", 4.7),
        ("Reliance Smart Point 441", "RETAIL", "reliancesmart441@okicici", "Pune", "Maharashtra", 4.6),
        ("Chai Point Express TechPark", "FOOD_BEVERAGE", "chaipoint.tp@okhdfcbank", "Hyderabad", "Telangana", 4.8),
        ("FabIndia Handlooms", "APPAREL", "fabindia.south@okaxis", "Chennai", "Tamil Nadu", 4.7),
        ("Croma Electronics Hub", "ELECTRONICS", "croma.store29@okicici", "Ahmedabad", "Gujarat", 4.9),
        ("MedPlus Superstore", "HEALTHCARE", "medplus.dlh@oksbi", "Gurugram", "Haryana", 4.5),
        ("Haldiram Food Planet", "FOOD_BEVERAGE", "haldirams.express@okhdfcbank", "Nagpur", "Maharashtra", 4.8),
        ("Zudio Fashion Trends", "APPAREL", "zudio.urban@okaxis", "Kolkata", "West Bengal", 4.4),
        ("Nature Basket Organic", "GROCERY", "naturesbasket@okicici", "Mumbai", "Maharashtra", 4.6),
        ("Decathlon Sports Depot", "RETAIL", "decathlon.in@okhdfcbank", "Bengaluru", "Karnataka", 4.9),
        ("Lenskart Opticals 102", "HEALTHCARE", "lenskart102@oksbi", "Jaipur", "Rajasthan", 4.7),
        ("Barbeque Nation Buffet", "FOOD_BEVERAGE", "bbqnation.res@okaxis", "Indore", "Madhya Pradesh", 4.6),
        ("Cafe Coffee Day Highway", "FOOD_BEVERAGE", "ccd.highway@okhdfcbank", "Coimbatore", "Tamil Nadu", 4.3),
        ("Crossword Bookstore", "RETAIL", "crossword.books@okicici", "Chandigarh", "Punjab", 4.8),
        ("Kalyan Jewellers Heritage", "JEWELRY", "kalyanjewellers@oksbi", "Kochi", "Kerala", 4.9),
        ("Titan Eye Plus Clinic", "HEALTHCARE", "titaneye.care@okaxis", "Lucknow", "Uttar Pradesh", 4.7),
        ("Subway Fresh Sandwiches", "FOOD_BEVERAGE", "subway.ft@okhdfcbank", "Noida", "Uttar Pradesh", 4.5),
        ("D Mart Hypermarket 09", "GROCERY", "dmart09@okicici", "Thane", "Maharashtra", 4.9)
    ], start=1)
]

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def create_jwt_token(sub: str, role: str, account_id: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": sub,
        "account_id": account_id,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(hours=2)).timestamp()),
        "iss": "sentinel-fintech-auth"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token_optional(authorization: Optional[str]) -> Optional[Dict[str, Any]]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None

# ==============================================================================
# SYSTEM HEALTH ENDPOINT
# ==============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": "fintech-dpi-target-cluster",
        "port": 8001,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# ==============================================================================
# 1. DOCUMENTED APIS (Present in OpenAPI Spec)
# ==============================================================================

@app.post("/api/v2/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(credentials: LoginRequest):
    """
    Authenticate retail or commercial banking user and issue JWT bearer token.
    """
    user_record = USERS_DB.get(credentials.username)
    if not user_record or user_record["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid banking credentials provided"
        )
    
    token = create_jwt_token(
        sub=credentials.username,
        role=user_record["role"],
        account_id=user_record["account_id"]
    )
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user={
            "sub": credentials.username,
            "account_id": user_record["account_id"],
            "name": user_record["name"],
            "role": user_record["role"],
            "email": user_record["email"]
        }
    )


@app.get("/api/v2/accounts/{account_id}/balance", response_model=AccountBalanceResponse, tags=["Accounts"])
async def get_account_balance(
    account_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Retrieve real-time account ledger balance.
    VULNERABILITY: Intentionally vulnerable to BOLA / IDOR.
    The service accepts a valid Bearer token from user A, but fails to verify
    whether JWT.sub or JWT.account_id matches the requested {account_id}.
    Any valid authenticated token can exfiltrate financial balances of other accounts.
    """
    # Find matching account by account_id in mock DB
    target_user = None
    for u in USERS_DB.values():
        if u["account_id"] == account_id or str(account_id) in u["account_id"]:
            target_user = u
            break

    if target_user:
        balance_val = target_user["balance"]
        holder_name = target_user["name"]
    else:
        # Deterministic fallback for ad-hoc account IDs (e.g., 9841, 1022) used by attack scripts
        seed = abs(hash(account_id)) % 1000000
        balance_val = round(seed + 1420.50, 2)
        holder_name = f"DPI User {account_id}"

    return AccountBalanceResponse(
        account_id=account_id,
        account_number=f"ACC-IN-{int(account_id):06d}" if account_id.isdigit() else f"ACC-IN-{account_id}",
        account_holder=holder_name,
        currency="INR",
        available_balance=balance_val,
        ledger_balance=balance_val,
        account_type="SAVINGS" if account_id != "999" else "TREASURY_ESCROW",
        status="ACTIVE",
        branch_ifsc="HDFC0001234",
        last_transaction=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


@app.get("/api/v2/directory/merchants", response_model=MerchantDirectoryResponse, tags=["Directory"])
async def list_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by merchant category")
):
    """
    Public directory of registered UPI & BharatQR merchants.
    Target endpoint for high-speed data scraping & harvesting attacks.
    """
    filtered = MERCHANTS_DB
    if category:
        filtered = [m for m in filtered if m["category"].upper() == category.upper()]

    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_data = [MerchantItem(**item) for item in filtered[start_idx:end_idx]]

    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return MerchantDirectoryResponse(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        data=page_data
    )


# ==============================================================================
# 2. ZOMBIE API (Deprecated v1 in spec, leaks sensitive Indian PII)
# ==============================================================================

@app.get(
    "/api/v1/users/export-all",
    response_model=List[PIIUserExport],
    deprecated=True,
    tags=["Legacy - Deprecated"]
)
async def export_all_users_legacy():
    """
    DEPRECATED V1 API (Zombie):
    Unauthenticated legacy migration endpoint that dumps synthetic Indian customer PII.
    Tagged with 'deprecated: true' in openapi_official.json.
    Exposes: PAN cards, UPI VPAs, Phone numbers, Emails, and Government ID references.
    """
    synthetic_pii_records = [
        PIIUserExport(
            user_id="USR-IN-101",
            full_name="Aarav Sharma",
            email="aarav.sharma@example.com",
            phone_number="+91-9876543210",
            pan_card="ABCDE1234F",
            upi_vpa="aarav.sharma@okhdfcbank",
            govt_id_reference="AADHAAR-XXXX-XXXX-9841",
            annual_income_inr=1850000.0,
            session_token_sample="eyJh...session_user101_sample_bearer_token"
        ),
        PIIUserExport(
            user_id="USR-IN-102",
            full_name="Priya Patel",
            email="priya.patel@example.com",
            phone_number="+91-9812345678",
            pan_card="BKRPK4829D",
            upi_vpa="priyapatel@okaxis",
            govt_id_reference="VOTER-ID-ABC1234567",
            annual_income_inr=3200000.0,
            session_token_sample="eyJh...session_user102_sample_bearer_token"
        ),
        PIIUserExport(
            user_id="USR-IN-103",
            full_name="Rohan Verma",
            email="rohan.verma@example.com",
            phone_number="+91-9723456789",
            pan_card="CPDPV9182M",
            upi_vpa="rohan.v@oksbi",
            govt_id_reference="AADHAAR-XXXX-XXXX-4412",
            annual_income_inr=850000.0,
            session_token_sample="eyJh...session_user103_sample_bearer_token"
        ),
        PIIUserExport(
            user_id="USR-IN-104",
            full_name="Ananya Iyer",
            email="ananya.iyer@example.com",
            phone_number="+91-9654321098",
            pan_card="DFEPI3391K",
            upi_vpa="ananya.iyer@okicici",
            govt_id_reference="PASSPORT-Z-8491023",
            annual_income_inr=4500000.0,
            session_token_sample="eyJh...session_user104_sample_bearer_token"
        )
    ]
    return synthetic_pii_records


# ==============================================================================
# 3. SHADOW APIS (Undocumented - excluded from openapi_official.json)
# ==============================================================================

@app.post("/api/internal/debug/reset", tags=["Shadow - Internal Debug"])
async def internal_debug_reset(payload: Optional[DebugResetRequest] = None):
    """
    UNDOCUMENTED SHADOW API:
    Internal developer debug endpoint left exposed in production.
    Not cataloged in openapi_official.json.
    """
    target = payload.target if payload else "all"
    return {
        "status": "acknowledged",
        "command": "DEBUG_SYSTEM_RESET",
        "target": target,
        "cluster_node": "node-fintech-worker-03.internal",
        "cache_evicted_keys": 42,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "warning": "Internal administrative route accessed without service mesh mTLS"
    }


@app.get("/api/internal/config/dump", tags=["Shadow - Internal Config"])
async def internal_config_dump():
    """
    UNDOCUMENTED SHADOW API:
    Unauthenticated configuration exposure endpoint.
    Leaked internal microservice infrastructure secrets, connection strings, and endpoints.
    Not cataloged in openapi_official.json.
    """
    return {
        "service_name": "fintech-dpi-core-banking",
        "environment": "staging-sandbox",
        "debug_mode": True,
        "cluster_region": "ap-south-1",
        "database_url": "postgresql://sentinel_admin:dummy_pass_placeholder@db-internal.mesh:5432/fintech_core",
        "internal_mesh_gateway": "http://mesh.internal.corp:8500",
        "jwt_algorithm": JWT_ALGORITHM,
        "kafka_brokers": [
            "kafka-broker-1.mesh:9092",
            "kafka-broker-2.mesh:9092"
        ],
        "redis_cache_host": "redis-cluster.mesh:6379",
        "circuit_breaker": {
            "failure_threshold": 5,
            "recovery_time_sec": 30
        },
        "build_version": "2.1.0-alpha-shadow"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("target_service.main:app", host="0.0.0.0", port=8001, reload=False)
