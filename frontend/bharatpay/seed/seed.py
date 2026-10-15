"""
BharatPay Comprehensive Realism & Synthetic Seed Script
Generates 18 realistic Indian users with believable financial profiles,
350+ verified merchants across 8 categories, and 300+ historical transactions.
Also provisions the Organization & Role Model: 6 distinct roles, 12 employees,
and sanctioned business campaigns.
All values are clearly synthetic test data for CC6-IC07 hackathon demo.
"""

import sys
import os
import json
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.models.account import Account
from app.models.upi import UPIProfile
from app.models.kyc import KYCRecord
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.models.organization import Role, Employee, AccessGrant, Campaign
from app.core.security import get_password_hash

SYNTHETIC_USERS = [
    {"user_code": "u_101", "name": "Priya Sharma", "email": "priya.sharma@bharatpay.com", "phone": "9876501001", "vpa": "priya.sharma@bharatpay", "balance_paise": 4850000, "pan": "ABCDE1234F", "aadhaar": "999988881001", "kyc": "VERIFIED", "region": "West"},
    {"user_code": "u_102", "name": "Rohit Verma", "email": "rohit.verma@bharatpay.com", "phone": "9876501002", "vpa": "rohit.verma@bharatpay", "balance_paise": 12500000, "pan": "BCDEF2345G", "aadhaar": "999988881002", "kyc": "VERIFIED", "region": "North"},
    {"user_code": "u_103", "name": "Ananya Iyer", "email": "ananya.iyer@bharatpay.com", "phone": "9876501003", "vpa": "ananya.iyer@bharatpay", "balance_paise": 1820000, "pan": "CDEFG3456H", "aadhaar": "999988881003", "kyc": "PENDING", "region": "South"},
    {"user_code": "u_104", "name": "Vikramaditya Rao", "email": "vikram.rao@bharatpay.com", "phone": "9876501004", "vpa": "vikram.rao@bharatpay", "balance_paise": 18500000, "pan": "DEFGH4567J", "aadhaar": "999988881004", "kyc": "VERIFIED", "region": "East"},
    {"user_code": "u_105", "name": "Sneha Patel", "email": "sneha.patel@bharatpay.com", "phone": "9876501005", "vpa": "sneha.patel@bharatpay", "balance_paise": 3240000, "pan": "EFGHI5678K", "aadhaar": "999988881005", "kyc": "VERIFIED", "region": "West"},
    {"user_code": "u_106", "name": "Arjun Kapoor", "email": "arjun.kapoor@bharatpay.com", "phone": "9876501006", "vpa": "arjun.kapoor@bharatpay", "balance_paise": 9400000, "pan": "FGHIJ6789L", "aadhaar": "999988881006", "kyc": "VERIFIED", "region": "North"},
    {"user_code": "u_107", "name": "Neha Deshmukh", "email": "neha.deshmukh@bharatpay.com", "phone": "9876501007", "vpa": "neha.deshmukh@bharatpay", "balance_paise": 1450000, "pan": "GHIJK7890M", "aadhaar": "999988881007", "kyc": "VERIFIED", "region": "West"},
    {"user_code": "u_108", "name": "Rahul Mehra", "email": "rahul.mehra@bharatpay.com", "phone": "9876501008", "vpa": "rahul.mehra@bharatpay", "balance_paise": 6200000, "pan": "HIJKL8901N", "aadhaar": "999988881008", "kyc": "VERIFIED", "region": "North"},
    {"user_code": "u_109", "name": "Deepika Sen", "email": "deepika.sen@bharatpay.com", "phone": "9876501009", "vpa": "deepika.sen@bharatpay", "balance_paise": 21000000, "pan": "IJKLM9012P", "aadhaar": "999988881009", "kyc": "VERIFIED", "region": "East"},
    {"user_code": "u_110", "name": "Karan Singhania", "email": "karan.singhania@bharatpay.com", "phone": "9876501010", "vpa": "karan.singhania@bharatpay", "balance_paise": 14500000, "pan": "JKLMN0123Q", "aadhaar": "999988881010", "kyc": "VERIFIED", "region": "North"},
    {"user_code": "u_111", "name": "Meera Nair", "email": "meera.nair@bharatpay.com", "phone": "9876501011", "vpa": "meera.nair@bharatpay", "balance_paise": 2890000, "pan": "KLMNO1234R", "aadhaar": "999988881011", "kyc": "VERIFIED", "region": "South"},
    {"user_code": "u_112", "name": "Aditya Joshi", "email": "aditya.joshi@bharatpay.com", "phone": "9876501012", "vpa": "aditya.joshi@bharatpay", "balance_paise": 7650000, "pan": "LMNOP2345S", "aadhaar": "999988881012", "kyc": "VERIFIED", "region": "West"},
    {"user_code": "u_113", "name": "Pooja Hegde", "email": "pooja.hegde@bharatpay.com", "phone": "9876501013", "vpa": "pooja.hegde@bharatpay", "balance_paise": 840000, "pan": "MNOPQ3456T", "aadhaar": "999988881013", "kyc": "PENDING", "region": "South"},
    {"user_code": "u_114", "name": "Siddharth Malhotra", "email": "sid.malhotra@bharatpay.com", "phone": "9876501014", "vpa": "sid.malhotra@bharatpay", "balance_paise": 11200000, "pan": "NOPQR4567U", "aadhaar": "999988881014", "kyc": "VERIFIED", "region": "North"},
    {"user_code": "u_115", "name": "Tanvi Kulkarni", "email": "tanvi.k@bharatpay.com", "phone": "9876501015", "vpa": "tanvi.k@bharatpay", "balance_paise": 5300000, "pan": "OPQRS5678V", "aadhaar": "999988881015", "kyc": "VERIFIED", "region": "West"},
    {"user_code": "u_116", "name": "Amitabh Sen", "email": "amitabh.sen@bharatpay.com", "phone": "9876501016", "vpa": "amitabh.sen@bharatpay", "balance_paise": 9100000, "pan": "PQRST6789W", "aadhaar": "999988881016", "kyc": "VERIFIED", "region": "East"},
    {"user_code": "u_117", "name": "Roshni Roy", "email": "roshni.roy@bharatpay.com", "phone": "9876501017", "vpa": "roshni.roy@bharatpay", "balance_paise": 3950000, "pan": "QRSTU7890X", "aadhaar": "999988881017", "kyc": "VERIFIED", "region": "East"},
    {"user_code": "u_118", "name": "Varun Dhawan", "email": "varun.dhawan@bharatpay.com", "phone": "9876501018", "vpa": "varun.dhawan@bharatpay", "balance_paise": 8820000, "pan": "RSTUV8901Y", "aadhaar": "999988881018", "kyc": "VERIFIED", "region": "North"},
]

ROLES_DATA = [
    {
        "role_name": "Employee (Support)",
        "level": 1,
        "default_scope": "support-tickets",
        "default_rate_limit": 150,
        "campaign_rate_limit": 250,
        "description": "Tier 1 Customer Support specialist — account lookup with required reason",
        "allowed_endpoints": ["/api/v2/internal/reports/account-lookup/{account_id}"]
    },
    {
        "role_name": "Sales Manager",
        "level": 2,
        "default_scope": "region",
        "default_rate_limit": 500,  # Up to 500 account lookups/day within their region
        "campaign_rate_limit": 2500,
        "description": "Regional Sales Manager — region-scoped sales and account queries",
        "allowed_endpoints": [
            "/api/v2/internal/reports/regional-sales",
            "/api/v2/internal/reports/account-lookup/{account_id}"
        ]
    },
    {
        "role_name": "Regional Head",
        "level": 3,
        "default_scope": "multi-region",
        "default_rate_limit": 1500,
        "campaign_rate_limit": 7500,
        "description": "Multi-regional oversight — aggregated regional reports and bulk export",
        "allowed_endpoints": [
            "/api/v2/internal/reports/regional-sales",
            "/api/v2/internal/reports/account-lookup/{account_id}",
            "/api/v2/internal/reports/bulk-export"
        ]
    },
    {
        "role_name": "VP Sales",
        "level": 4,
        "default_scope": "org-wide",
        "default_rate_limit": 200,   # 200/day normally; up to 5,000/day during an active campaign
        "campaign_rate_limit": 5000,
        "description": "VP of Sales — org-wide executive summaries, elevated volume during campaigns",
        "allowed_endpoints": [
            "/api/v2/internal/reports/regional-sales",
            "/api/v2/internal/reports/account-lookup/{account_id}",
            "/api/v2/internal/reports/org-wide-summary",
            "/api/v2/internal/reports/bulk-export"
        ]
    },
    {
        "role_name": "IT Admin",
        "level": 5,
        "default_scope": "ops-only",
        "default_rate_limit": 1000,
        "campaign_rate_limit": 2000,
        "description": "IT Administrator — employee onboarding, campaign registration, access audit",
        "allowed_endpoints": [
            "/api/v2/internal/employees/onboard",
            "/api/v2/internal/campaigns",
            "/api/v2/internal/employees/{id}/access-log"
        ]
    },
    {
        "role_name": "Customer",
        "level": 0,
        "default_scope": "none",
        "default_rate_limit": 100,
        "campaign_rate_limit": 100,
        "description": "Retail customer — no internal access",
        "allowed_endpoints": []
    }
]

EMPLOYEES_DATA = [
    {
        "employee_id": "EMP-1001",
        "name": "Rajesh Sharma",
        "email": "rajesh.sharma@corp.bharatpay.com",
        "role": "IT Admin",
        "department": "IT Ops",
        "region": "IT-Infra",
        "manager_id": None,
        "hire_days_ago": 365
    },
    {
        "employee_id": "EMP-1002",
        "name": "Sunita Rao",
        "email": "sunita.rao@corp.bharatpay.com",
        "role": "VP Sales",
        "department": "Sales",
        "region": "org-wide",
        "manager_id": "EMP-1001",
        "hire_days_ago": 240
    },
    {
        "employee_id": "EMP-1003",
        "name": "Vikram Malhotra",
        "email": "vikram.malhotra@corp.bharatpay.com",
        "role": "Regional Head",
        "department": "Sales",
        "region": "North",
        "manager_id": "EMP-1002",
        "hire_days_ago": 180
    },
    {
        "employee_id": "EMP-1004",
        "name": "Lakshmi Narayanan",
        "email": "lakshmi.n@corp.bharatpay.com",
        "role": "Regional Head",
        "department": "Sales",
        "region": "South",
        "manager_id": "EMP-1002",
        "hire_days_ago": 160
    },
    {
        "employee_id": "EMP-1005",
        "name": "Amit Banerjee",
        "email": "amit.banerjee@corp.bharatpay.com",
        "role": "Regional Head",
        "department": "Sales",
        "region": "East",
        "manager_id": "EMP-1002",
        "hire_days_ago": 150
    },
    {
        "employee_id": "EMP-1006",
        "name": "Sanjay Patel",
        "email": "sanjay.patel@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "West",
        "manager_id": "EMP-1002",
        "hire_days_ago": 120
    },
    {
        "employee_id": "EMP-1007",
        "name": "Pooja Joshi",
        "email": "pooja.joshi@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "North",
        "manager_id": "EMP-1003",
        "hire_days_ago": 90
    },
    {
        "employee_id": "EMP-1008",
        "name": "Karthik Sundaram",
        "email": "karthik.s@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "South",
        "manager_id": "EMP-1004",
        "hire_days_ago": 75
    },
    {
        "employee_id": "EMP-1009",
        "name": "Debashish Roy",
        "email": "debashish.roy@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "East",
        "manager_id": "EMP-1005",
        "hire_days_ago": 60
    },
    {
        "employee_id": "EMP-1010",
        "name": "Neha Gupta",
        "email": "neha.gupta@corp.bharatpay.com",
        "role": "Employee (Support)",
        "department": "Customer Support",
        "region": "org-wide",
        "manager_id": "EMP-1006",
        "hire_days_ago": 45
    },
    {
        "employee_id": "EMP-1011",
        "name": "Manoj Tiwari",
        "email": "manoj.tiwari@corp.bharatpay.com",
        "role": "Employee (Support)",
        "department": "Customer Support",
        "region": "North",
        "manager_id": "EMP-1007",
        "hire_days_ago": 30
    },
    {
        "employee_id": "EMP-1012",
        "name": "Ananya Mukherjee",
        "email": "ananya.m@corp.bharatpay.com",
        "role": "Employee (Support)",
        "department": "Customer Support",
        "region": "East",
        "manager_id": "EMP-1009",
        "hire_days_ago": 5  # Fresh hire (within 14 days) for grace profile testing
    }
]

def seed_organization(db):
    print("[BharatPay Seed] Seeding privileged organization roles...")
    role_map = {}
    for rdata in ROLES_DATA:
        role = db.query(Role).filter(Role.role_name == rdata["role_name"]).first()
        if not role:
            role = Role(
                role_name=rdata["role_name"],
                level=rdata["level"],
                default_scope=rdata["default_scope"],
                default_rate_limit=rdata["default_rate_limit"],
                campaign_rate_limit=rdata["campaign_rate_limit"],
                description=rdata["description"],
                allowed_endpoints_json=json.dumps(rdata["allowed_endpoints"])
            )
            db.add(role)
            db.flush()
        else:
            role.level = rdata["level"]
            role.default_scope = rdata["default_scope"]
            role.default_rate_limit = rdata["default_rate_limit"]
            role.campaign_rate_limit = rdata["campaign_rate_limit"]
            role.description = rdata["description"]
            role.allowed_endpoints_json = json.dumps(rdata["allowed_endpoints"])
        role_map[rdata["role_name"]] = role

    db.commit()

    print("[BharatPay Seed] Seeding 12 provisioned employees with departmental hierarchy...")
    emp_pwd_hash = get_password_hash("Employee@123")
    now = datetime.now(timezone.utc)

    for edata in EMPLOYEES_DATA:
        emp = db.query(Employee).filter(Employee.employee_id == edata["employee_id"]).first()
        hire_date = now - timedelta(days=edata["hire_days_ago"])
        role_obj = role_map[edata["role"]]
        if not emp:
            emp = Employee(
                employee_id=edata["employee_id"],
                name=edata["name"],
                email=edata["email"],
                hashed_password=emp_pwd_hash,
                role_id=role_obj.id,
                department=edata["department"],
                region=edata["region"],
                manager_id=edata["manager_id"],
                status="ACTIVE",
                hire_date=hire_date
            )
            db.add(emp)
        else:
            emp.name = edata["name"]
            emp.email = edata["email"]
            emp.role_id = role_obj.id
            emp.department = edata["department"]
            emp.region = edata["region"]
            emp.manager_id = edata["manager_id"]
            emp.hire_date = hire_date

    db.commit()

    # Seed baseline active campaigns
    campaign_data = [
        {
            "campaign_code": "CAMP-DIWALI-2026",
            "name": "Diwali Sale 2026",
            "start_date": now - timedelta(days=2),
            "end_date": now + timedelta(days=7),
            "affected_regions": ["West", "North", "South", "East", "org-wide"],
            "expected_roles": ["VP Sales", "Regional Head", "Sales Manager"],
            "expected_volume_multiplier": 10,
            "created_by": "EMP-1001"
        },
        {
            "campaign_code": "CAMP-HOLI-2027",
            "name": "Holi Cashback Dhamaka",
            "start_date": now - timedelta(days=1),
            "end_date": now + timedelta(days=6),
            "affected_regions": ["North", "West", "East", "org-wide"],
            "expected_roles": ["VP Sales", "Regional Head", "Sales Manager"],
            "expected_volume_multiplier": 8,
            "created_by": "EMP-1001"
        },
        {
            "campaign_code": "CAMP-FY-END-2027",
            "name": "Fiscal Year-End Surge",
            "start_date": now - timedelta(days=3),
            "end_date": now + timedelta(days=12),
            "affected_regions": ["org-wide", "West", "South", "North", "East"],
            "expected_roles": ["VP Sales", "Regional Head"],
            "expected_volume_multiplier": 6,
            "created_by": "EMP-1002"
        },
        {
            "campaign_code": "CAMP-REPUBLIC-2027",
            "name": "Republic Day Merchant Fest",
            "start_date": now - timedelta(days=1),
            "end_date": now + timedelta(days=5),
            "affected_regions": ["South", "West", "North"],
            "expected_roles": ["Regional Head", "Sales Manager"],
            "expected_volume_multiplier": 5,
            "created_by": "EMP-1001"
        }
    ]

    for cdata in campaign_data:
        campaign = db.query(Campaign).filter(Campaign.campaign_code == cdata["campaign_code"]).first()
        if not campaign:
            campaign = Campaign(
                campaign_code=cdata["campaign_code"],
                name=cdata["name"],
                start_date=cdata["start_date"],
                end_date=cdata["end_date"],
                affected_regions_json=json.dumps(cdata["affected_regions"]),
                expected_roles_json=json.dumps(cdata["expected_roles"]),
                expected_volume_multiplier=cdata["expected_volume_multiplier"],
                created_by=cdata["created_by"]
            )
            db.add(campaign)
        else:
            campaign.name = cdata["name"]
            campaign.start_date = cdata["start_date"]
            campaign.end_date = cdata["end_date"]
            campaign.affected_regions_json = json.dumps(cdata["affected_regions"])
            campaign.expected_roles_json = json.dumps(cdata["expected_roles"])
            campaign.expected_volume_multiplier = cdata["expected_volume_multiplier"]
    db.commit()
    print("[BharatPay Seed] Organization & all campaign windows seeded successfully!")


def seed_database():
    print("[BharatPay Seed] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed Organization structure first
        seed_organization(db)

        # Check current user count
        current_users_count = db.query(User).count()
        if current_users_count >= 18 and db.query(Merchant).count() >= 200:
            # Update regions on existing accounts if needed
            for i, udata in enumerate(SYNTHETIC_USERS, 1):
                user = db.query(User).filter(User.user_code == udata["user_code"]).first()
                if user:
                    acc = db.query(Account).filter(Account.user_id == user.id).first()
                    if acc:
                        acc.region = udata.get("region", "West")
            db.commit()
            print(f"[BharatPay Seed] Database already seeded with {current_users_count} users.")
            return

        print("[BharatPay Seed] Seeding 18 synthetic Indian users with realistic accounts...")
        default_pwd_hash = get_password_hash("Password@123")

        created_accounts = []
        for i, udata in enumerate(SYNTHETIC_USERS, 1):
            user = db.query(User).filter(User.user_code == udata["user_code"]).first()
            if not user:
                user = User(
                    user_code=udata["user_code"],
                    full_name=udata["name"],
                    email=udata["email"],
                    phone=udata["phone"],
                    hashed_password=default_pwd_hash,
                    role="customer"
                )
                db.add(user)
                db.flush()

                acc_num = f"50100234{1000 + i:04d}"
                masked_acc = f"XXXXXXXX{1000 + i:04d}"

                account = Account(
                    user_id=user.id,
                    account_number=acc_num,
                    masked_account_number=masked_acc,
                    ifsc_code="BPAY0001042",
                    region=udata.get("region", "West"),
                    balance_paise=udata["balance_paise"],
                    daily_limit_paise=10000000,  # ₹1,00,000.00
                    currency="INR",
                    status="ACTIVE"
                )
                db.add(account)
                db.flush()

                upi = UPIProfile(
                    user_id=user.id,
                    account_id=account.id,
                    vpa=udata["vpa"],
                    is_primary=True,
                    status="ACTIVE"
                )
                db.add(upi)

                masked_pan = f"{udata['pan'][:5]}****{udata['pan'][-1]}"
                masked_aadhaar = f"XXXXXXXX{udata['aadhaar'][-4:]}"

                kyc = KYCRecord(
                    user_id=user.id,
                    pan_synthetic=udata["pan"],
                    masked_pan=masked_pan,
                    aadhaar_synthetic=udata["aadhaar"],
                    masked_aadhaar=masked_aadhaar,
                    kyc_status=udata["kyc"],
                    verified_at=datetime.now(timezone.utc) if udata["kyc"] == "VERIFIED" else None
                )
                db.add(kyc)
                created_accounts.append((user, account))
            else:
                account = db.query(Account).filter(Account.user_id == user.id).first()
                if account:
                    account.region = udata.get("region", "West")
                created_accounts.append((user, account))

        db.commit()
        print(f"[BharatPay Seed] Successfully verified {len(created_accounts)} user accounts.")

        # Seed realistic merchants across 8 categories
        print("[BharatPay Seed] Generating 350+ realistic Indian merchants...")
        merchant_categories = [
            ("Swiggy / Zomato Food & Dining", ["Biryani by Kilo", "Haldiram's", "Faasos", "Behrouz Biryani", "Barbeque Nation", "Wow! Momo", "Burger Singh", "Chai Point", "Chaayos", "Bikanervala", "Saravanaa Bhavan", "Empire Restaurant", "Paradise Biryani", "Sagar Ratna", "Social Offline", "Farzi Cafe", "Mainland China", "Keventers", "Naturals Ice Cream", "Theobroma"]),
            ("Grocery & Daily Essentials", ["Blinkit Mart", "Zepto Express", "Instamart Store", "Nature's Basket", "More Retail", "DMart Ready", "Spencer's Retail", "Modern Bazaar", "Ratnadeep Supermarket", "MK Retail", "Star Bazaar", "Easyday Club", "Heritage Fresh", "Apollo Pharmacy", "MedPlus Mart", "Wellness Forever", "Netmeds Store", "1mg Wellness", "Pharmeasy Store", "HealthKart"]),
            ("E-Commerce & Fashion", ["Flipkart Internet", "Amazon India", "Myntra Designs", "Nykaa E-Retail", "Ajio Trends", "Tata CLiQ", "Croma Digital", "Vijay Sales", "Reliance Digital", "Lenskart Solutions", "Boat Lifestyle", "Noise Wearables", "Zudio Retail", "Max Fashion", "Westside Store", "Fabindia Overseas", "Bata India", "Wildcraft India", "Snitch Menswear", "Bewakoof Brands"]),
            ("Travel & Commute", ["Uber India", "Ola Cabs", "Rapido Bike Taxi", "MakeMyTrip India", "Goibibo Travel", "IRCTC Ticketing", "Yatra Online", "RedBus India", "IndiGo Airlines", "Air India Express", "Cleartrip Pvt Ltd", "AbhiBus", "Zoomcar India", "Bounce Mobility", "Chalo Mobility", "Delhi Metro Rail", "Namma Metro BMRCL", "Maha Mumbai Metro", "Fastag Toll NHAI", "Indian Oil Fuel"]),
            ("Utilities & Telecommunications", ["Jio Prepaid / Postpaid", "Airtel Telecommunications", "Vodafone Idea Vi", "BSNL Broadband", "Tata Power DDL", "BSES Rajdhani", "Adani Electricity Mumbai", "Bescom Bengaluru", "MSEDCL Maharashtra", "Torrent Power", "Indraprastha Gas IGL", "Mahanagar Gas MGL", "Gujarat Gas", "ACT Fibernet", "Hathaway Cable", "Tata Sky / Tata Play", "Dish TV India", "Sun Direct", "Airtel DTH", "Municipal Water Corp"]),
            ("Entertainment & Streaming", ["BookMyShow Tickets", "PVR INOX Cinemas", "Netflix India", "Disney+ Hotstar", "Spotify India", "YouTube Premium", "SonyLIV", "Zee5 Global", "Apple India Services", "Google Play Store", "Amazon Prime Video", "JioCinema Premium", "Gaana Music", "Wynk Music", "Audible India", "Cinepolis India", "Carnival Cinemas", "Miraj Cinemas", "Sony Pictures", "Paytm Insider Events"]),
            ("Education & Learning", ["Unacademy Edu", "Physics Wallah PW", "Coursera Learning", "Udemy Global", "Simplilearn Solutions", "Scaler Academy", "UpGrad Education", "Eruditus Exec Ed", "Allen Career Institute", "Aakash Institute", "FIITJEE Delhi", "Vedantu Innovations", "BYJU'S Learning", "Khan Academy India", "Duolingo Plus", "Testbook Edu", "Adda247 Online", "Classplus Edu", "Unstop Platform", "Internshala Trainings"]),
            ("Local Services & Artisans", ["Urban Company Services", "Wakefit Innovations", "Pepperfry Home", "Livspace Interiors", "HomeLane Decor", "NoBroker Services", "MagicBricks Realty", "Dunzo Express", "Porter Logistics", "Shadowfax Delivery", "Delhivery Direct", "Blue Dart Express", "DTDC Courier", "CleanCraft Drycleaners", "Kaya Skin Clinic", "VLCC Healthcare", "Looks Salon", "Enrich Beauty", "Jawad Habib Hair", "Toni&Guy India"])
        ]

        merchants_to_add = []
        m_count = 0
        for category, brand_names in merchant_categories:
            for name in brand_names:
                m_count += 1
                clean_name = name.lower().replace(" ", "").replace("'", "").replace("+", "plus").replace("/", "")
                vpa = f"{clean_name}@bpaymerchant"
                m_code = f"m_{m_count:04d}"
                rating = round(random.uniform(4.2, 4.95), 2)
                merchants_to_add.append(
                    Merchant(
                        merchant_code=m_code,
                        business_name=name,
                        vpa=vpa,
                        category=category,
                        verified=True,
                        rating=rating
                    )
                )

        # Pad remaining merchants to 350+
        suffixes = ["Ventures", "Enterprises", "Retail", "Services", "Hub", "Corner", "Mart", "Express"]
        indian_cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
        while m_count < 356:
            m_count += 1
            city = random.choice(indian_cities)
            suffix = random.choice(suffixes)
            cat_tuple = random.choice(merchant_categories)
            cat = cat_tuple[0]
            b_name = f"{city} {cat.split()[0]} {suffix}"
            clean = b_name.lower().replace(" ", "")
            vpa = f"{clean}_{m_count}@bpaymerchant"
            merchants_to_add.append(
                Merchant(
                    merchant_code=f"m_{m_count:04d}",
                    business_name=b_name,
                    vpa=vpa,
                    category=cat,
                    verified=True,
                    rating=round(random.uniform(4.0, 4.8), 2)
                )
            )

        db.bulk_save_objects(merchants_to_add)
        db.commit()
        print(f"[BharatPay Seed] Successfully seeded {db.query(Merchant).count()} merchants.")

        # Seed 300+ realistic historical transactions
        print("[BharatPay Seed] Generating 300+ historical transactions...")
        user_accounts = db.query(Account).all()
        merchants = db.query(Merchant).all()

        common_spending = [
            ("Swiggy Online Food", "swiggy@bpaymerchant", 18900, 65000),
            ("Zepto Daily Groceries", "zeptoexpress@bpaymerchant", 12000, 89000),
            ("Uber Trip Payment", "uberindia@bpaymerchant", 9500, 45000),
            ("Blinkit Instant Mart", "blinkitmart@bpaymerchant", 25000, 115000),
            ("Amazon Marketplace", "amazonindia@bpaymerchant", 49900, 399900),
            ("Myntra Fashion Order", "myntradesigns@bpaymerchant", 89900, 249900),
            ("Starbucks Coffee / Tata", "socialoffline@bpaymerchant", 25000, 75000),
            ("Airtel Monthly Broadband", "airteltelecommunications@bpaymerchant", 79900, 149900),
            ("BookMyShow Cinema Tickets", "bookmyshowtickets@bpaymerchant", 40000, 120000),
            ("Apollo Pharmacy Medicines", "apollopharmacy@bpaymerchant", 15000, 95000),
        ]

        now = datetime.now(timezone.utc)
        txn_idx = 0

        for user, account in created_accounts:
            num_txns = random.randint(15, 20)
            for _ in range(num_txns):
                txn_idx += 1
                days_ago = random.randint(1, 60)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                txn_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

                if random.random() < 0.8:
                    note, to_vpa, min_p, max_p = random.choice(common_spending)
                    amount_paise = random.randint(min_p, max_p)
                    recipient_acc_id = None
                else:
                    other_user, other_acc = random.choice([u for u in created_accounts if u[0].id != user.id])
                    to_vpa = other_user.upi_profiles[0].vpa if other_user.upi_profiles else f"{other_user.user_code}@bharatpay"
                    note = random.choice(["Dinner split", "Cab share", "Weekend trip", "Gift", "Repayment"])
                    amount_paise = random.randint(50000, 250000)
                    recipient_acc_id = other_acc.id

                txn = Transaction(
                    txn_reference=f"TXN2026{days_ago:02d}{txn_idx:05d}",
                    from_account_id=account.id,
                    to_account_id=recipient_acc_id,
                    from_vpa=user.upi_profiles[0].vpa if user.upi_profiles else f"{user.user_code}@bharatpay",
                    to_vpa=to_vpa,
                    amount_paise=amount_paise,
                    note=note,
                    status="SUCCESS",
                    created_at=txn_time
                )
                db.add(txn)

        db.commit()
        print(f"[BharatPay Seed] Successfully seeded {db.query(Transaction).count()} transactions across all users.")
        print("[BharatPay Seed] Realism pass complete!")

    except Exception as e:
        db.rollback()
        print(f"[BharatPay Seed] Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
