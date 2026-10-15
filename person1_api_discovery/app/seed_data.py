"""
Seed data module for Person 1: FinTech DPI Test Banking Service.
Generates 25 realistic accounts (user_1001 to user_1025) with synthetic Indian PII,
merchants, IFSC directory, transaction ledgers, and internal config state.
"""

from typing import Dict, List, Any

# First and last names for realistic Indian banking profiles
INDIAN_NAMES = [
    ("Aarav", "Sharma"), ("Priya", "Patel"), ("Rohan", "Verma"), ("Ananya", "Iyer"),
    ("Vikram", "Reddy"), ("Neha", "Gupta"), ("Arjun", "Nair"), ("Pooja", "Mehta"),
    ("Aditya", "Joshi"), ("Kavya", "Deshmukh"), ("Siddharth", "Rao"), ("Sneha", "Kulkarni"),
    ("Rahul", "Chopra"), ("Divya", "Menon"), ("Kabir", "Bose"), ("Meera", "Sen"),
    ("Varun", "Saxena"), ("Tanvi", "Bhatia"), ("Karan", "Singhania"), ("Ishita", "Malhotra"),
    ("Gaurav", "Pandey"), ("Shreya", "Agarwal"), ("Nikhil", "Trivedi"), ("Ritu", "Dubey"),
    ("Aakash", "Mishra")
]

USERS_DB: Dict[str, Dict[str, Any]] = {}
ACCOUNTS_DB: Dict[str, Dict[str, Any]] = {}
TRANSACTIONS_DB: Dict[str, List[Dict[str, Any]]] = {}
RECEIPTS_DB: Dict[str, Dict[str, Any]] = {}
BENEFICIARIES_DB: Dict[str, List[Dict[str, Any]]] = {}
SCHEDULED_PAYMENTS_DB: List[Dict[str, Any]] = []

# Generate 25 seeded users and accounts
for i in range(1, 26):
    account_num = 1000 + i
    user_id = f"user_{account_num}"
    first, last = INDIAN_NAMES[i - 1]
    full_name = f"{first} {last}"
    
    # Strictly synthetic PII placeholders
    pan = f"ABCDE{account_num}F"
    govt_id_like = f"[GOVT-ID-XXXX-{account_num}]"
    phone = f"+91-98765{account_num:05d}"
    upi_vpa = f"{user_id}@okaxis"
    email = f"{first.lower()}.{last.lower()}@examplebank.in"
    role = "admin" if i == 25 else "customer"
    balance = round(45000.0 + (i * 3250.75), 2)
    ifsc = "HDFC0001234" if i % 2 == 0 else "SBIN0000456"

    USERS_DB[user_id] = {
        "user_id": user_id,
        "username": user_id,
        "password": "pass123",
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "pan": pan,
        "govt_id_like": govt_id_like,
        "upi_vpa": upi_vpa,
        "role": role,
        "account_id": str(account_num)
    }

    ACCOUNTS_DB[str(account_num)] = {
        "account_id": str(account_num),
        "user_id": user_id,
        "account_number": f"ACCN-IN-{account_num}",
        "account_holder": full_name,
        "currency": "INR",
        "available_balance": balance,
        "ledger_balance": balance,
        "account_type": "SAVINGS" if i % 3 != 0 else "CURRENT",
        "status": "ACTIVE",
        "ifsc_code": ifsc,
        "branch_name": "Nariman Point Branch" if i % 2 == 0 else "Indiranagar Branch",
        "pan": pan,
        "govt_id_like": govt_id_like,
        "created_at": "2024-01-15T10:00:00Z"
    }

    # Generate 3 transactions per account
    txns = []
    for t_idx in range(1, 4):
        txn_id = f"TXN{account_num}{t_idx:02d}"
        amount = round(120.0 * (t_idx + i), 2)
        txn_type = "CREDIT" if t_idx == 1 else "DEBIT"
        description = "Salary Deposit" if t_idx == 1 else ("Merchant UPI QR" if t_idx == 2 else "Utility Bill")
        
        txn_record = {
            "txn_id": txn_id,
            "account_id": str(account_num),
            "amount": amount,
            "type": txn_type,
            "description": description,
            "reference_number": f"REF-DPI-{account_num}-{t_idx}",
            "status": "COMPLETED",
            "timestamp": f"2026-10-{10 + t_idx}T14:30:00Z"
        }
        txns.append(txn_record)

        RECEIPTS_DB[txn_id] = {
            "receipt_id": f"RCP-{txn_id}",
            "txn_id": txn_id,
            "account_id": str(account_num),
            "amount": amount,
            "currency": "INR",
            "sender_upi": upi_vpa,
            "beneficiary_name": "Bharat Merchant Pay" if txn_type == "DEBIT" else "Corporate Payroll",
            "tax_invoice_no": f"INV-GSTIN-{account_num}",
            "pan_masked": pan,
            "status": "SUCCESS",
            "issued_at": f"2026-10-{10 + t_idx}T14:31:00Z"
        }

    TRANSACTIONS_DB[str(account_num)] = txns

    # Seed beneficiaries
    BENEFICIARIES_DB[str(account_num)] = [
        {
            "beneficiary_id": f"BEN-{account_num}-1",
            "name": f"{INDIAN_NAMES[(i) % 25][0]} {INDIAN_NAMES[(i) % 25][1]}",
            "account_number": f"ACCN-IN-{1000 + ((i % 25) + 1)}",
            "ifsc": "HDFC0001234",
            "upi_vpa": f"user_{1000 + ((i % 25) + 1)}@okaxis",
            "status": "VERIFIED"
        }
    ]

# Seed Scheduled Payments (Intentionally UNUSED in standard traffic)
SCHEDULED_PAYMENTS_DB = [
    {
        "schedule_id": "SCHED-9001",
        "account_id": "1001",
        "amount": 2500.00,
        "frequency": "MONTHLY",
        "beneficiary_upi": "rent.landlord@okaxis",
        "next_execution": "2026-11-01T00:00:00Z",
        "status": "SCHEDULED"
    },
    {
        "schedule_id": "SCHED-9002",
        "account_id": "1002",
        "amount": 850.00,
        "frequency": "MONTHLY",
        "beneficiary_upi": "broadband.fiber@okhdfcbank",
        "next_execution": "2026-11-05T00:00:00Z",
        "status": "SCHEDULED"
    }
]

# Seed Merchants (Target for data scraping)
MERCHANTS_DIRECTORY: List[Dict[str, Any]] = [
    {"merchant_id": f"MRC-{i:03d}",
     "name": name,
     "category": cat,
     "upi_vpa": upi,
     "city": city,
     "rating": rate,
     "active": True}
    for i, (name, cat, upi, city, rate) in enumerate([
        ("Sharma Kirana & General Store", "GROCERY", "sharmakiran@okhdfcbank", "Mumbai", 4.8),
        ("Apollo Pharmacy Partner 104", "HEALTHCARE", "apollomeds@okaxis", "Bengaluru", 4.9),
        ("Bikanervala Sweets & Snacks", "FOOD_BEVERAGE", "bikanervala@oksbi", "New Delhi", 4.7),
        ("Reliance Smart Point 441", "RETAIL", "reliancesmart441@okicici", "Pune", 4.6),
        ("Chai Point Express TechPark", "FOOD_BEVERAGE", "chaipoint.tp@okhdfcbank", "Hyderabad", 4.8),
        ("FabIndia Handlooms South", "APPAREL", "fabindia.south@okaxis", "Chennai", 4.7),
        ("Croma Electronics Hub 29", "ELECTRONICS", "croma.store29@okicici", "Ahmedabad", 4.9),
        ("MedPlus Superstore CyberCity", "HEALTHCARE", "medplus.dlh@oksbi", "Gurugram", 4.5),
        ("Haldiram Food Planet Express", "FOOD_BEVERAGE", "haldirams.express@okhdfcbank", "Nagpur", 4.8),
        ("Zudio Urban Trends Mall", "APPAREL", "zudio.urban@okaxis", "Kolkata", 4.4),
        ("Nature Basket Organic Gourmet", "GROCERY", "naturesbasket@okicici", "Mumbai", 4.6),
        ("Decathlon Sports Warehouse", "RETAIL", "decathlon.in@okhdfcbank", "Bengaluru", 4.9),
        ("Lenskart Opticals 102", "HEALTHCARE", "lenskart102@oksbi", "Jaipur", 4.7),
        ("Barbeque Nation Buffet Express", "FOOD_BEVERAGE", "bbqnation.res@okaxis", "Indore", 4.6),
        ("Cafe Coffee Day Highway Point", "FOOD_BEVERAGE", "ccd.highway@okhdfcbank", "Coimbatore", 4.3),
        ("Crossword Bookstore & Stationery", "RETAIL", "crossword.books@okicici", "Chandigarh", 4.8),
        ("Kalyan Jewellers Heritage Line", "JEWELRY", "kalyanjewellers@oksbi", "Kochi", 4.9),
        ("Titan Eye Plus Care Clinic", "HEALTHCARE", "titaneye.care@okaxis", "Lucknow", 4.7),
        ("Subway Fresh Sandwiches Hub", "FOOD_BEVERAGE", "subway.ft@okhdfcbank", "Noida", 4.5),
        ("D Mart Hypermarket 09 Central", "GROCERY", "dmart09@okicici", "Thane", 4.9),
        ("BigBasket Quick Darkstore", "GROCERY", "bbdaily.wh@okaxis", "Bengaluru", 4.8),
        ("Blinkit Instant Mart 82", "GROCERY", "blinkit.hub82@okhdfcbank", "Delhi", 4.7),
        ("Zepto Delivery Station 11", "GROCERY", "zepto.ds11@oksbi", "Mumbai", 4.8),
        ("Keventers Milkshakes Express", "FOOD_BEVERAGE", "keventers@okicici", "Gurugram", 4.4),
        ("Mamaearth Organic Store", "RETAIL", "mamaearth@okaxis", "Noida", 4.6)
    ], start=1)
]

# Seed IFSC Directory (Public / No Auth #1)
IFSC_DIRECTORY: Dict[str, Dict[str, Any]] = {
    "HDFC0001234": {
        "ifsc_code": "HDFC0001234",
        "bank_name": "HDFC Bank",
        "branch": "Nariman Point",
        "city": "Mumbai",
        "state": "Maharashtra",
        "rtgs": True,
        "neft": True,
        "imps": True,
        "upi": True
    },
    "SBIN0000456": {
        "ifsc_code": "SBIN0000456",
        "bank_name": "State Bank of India",
        "branch": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "rtgs": True,
        "neft": True,
        "imps": True,
        "upi": True
    },
    "ICIC0000890": {
        "ifsc_code": "ICIC0000890",
        "bank_name": "ICICI Bank",
        "branch": "Connaught Place",
        "city": "New Delhi",
        "state": "Delhi",
        "rtgs": True,
        "neft": True,
        "imps": True,
        "upi": True
    },
    "YESB0001001": {
        "ifsc_code": "YESB0001001",
        "bank_name": "Yes Bank",
        "branch": "Bandra Kurla Complex",
        "city": "Mumbai",
        "state": "Maharashtra",
        "rtgs": True,
        "neft": True,
        "imps": True,
        "upi": True
    }
}
