"""
BharatPay Comprehensive Realism & Synthetic Seed Script
Generates 18 realistic Indian users with believable financial profiles,
350+ verified merchants across 8 categories, and 300+ historical transactions.
All values are clearly synthetic test data for CC6-IC07 hackathon demo.
"""

import sys
import os
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
from app.core.security import get_password_hash

SYNTHETIC_USERS = [
    {"user_code": "u_101", "name": "Priya Sharma", "email": "priya.sharma@bharatpay.com", "phone": "9876501001", "vpa": "priya.sharma@bharatpay", "balance_paise": 4850000, "pan": "ABCDE1234F", "aadhaar": "999988881001", "kyc": "VERIFIED"},
    {"user_code": "u_102", "name": "Rohit Verma", "email": "rohit.verma@bharatpay.com", "phone": "9876501002", "vpa": "rohit.verma@bharatpay", "balance_paise": 12500000, "pan": "BCDEF2345G", "aadhaar": "999988881002", "kyc": "VERIFIED"},
    {"user_code": "u_103", "name": "Ananya Iyer", "email": "ananya.iyer@bharatpay.com", "phone": "9876501003", "vpa": "ananya.iyer@bharatpay", "balance_paise": 1820000, "pan": "CDEFG3456H", "aadhaar": "999988881003", "kyc": "PENDING"},
    {"user_code": "u_104", "name": "Vikramaditya Rao", "email": "vikram.rao@bharatpay.com", "phone": "9876501004", "vpa": "vikram.rao@bharatpay", "balance_paise": 18500000, "pan": "DEFGH4567J", "aadhaar": "999988881004", "kyc": "VERIFIED"},
    {"user_code": "u_105", "name": "Sneha Patel", "email": "sneha.patel@bharatpay.com", "phone": "9876501005", "vpa": "sneha.patel@bharatpay", "balance_paise": 3240000, "pan": "EFGHI5678K", "aadhaar": "999988881005", "kyc": "VERIFIED"},
    {"user_code": "u_106", "name": "Arjun Kapoor", "email": "arjun.kapoor@bharatpay.com", "phone": "9876501006", "vpa": "arjun.kapoor@bharatpay", "balance_paise": 9400000, "pan": "FGHIJ6789L", "aadhaar": "999988881006", "kyc": "VERIFIED"},
    {"user_code": "u_107", "name": "Neha Deshmukh", "email": "neha.deshmukh@bharatpay.com", "phone": "9876501007", "vpa": "neha.deshmukh@bharatpay", "balance_paise": 1450000, "pan": "GHIJK7890M", "aadhaar": "999988881007", "kyc": "VERIFIED"},
    {"user_code": "u_108", "name": "Rahul Mehra", "email": "rahul.mehra@bharatpay.com", "phone": "9876501008", "vpa": "rahul.mehra@bharatpay", "balance_paise": 6200000, "pan": "HIJKL8901N", "aadhaar": "999988881008", "kyc": "VERIFIED"},
    {"user_code": "u_109", "name": "Deepika Sen", "email": "deepika.sen@bharatpay.com", "phone": "9876501009", "vpa": "deepika.sen@bharatpay", "balance_paise": 21000000, "pan": "IJKLM9012P", "aadhaar": "999988881009", "kyc": "VERIFIED"},
    {"user_code": "u_110", "name": "Karan Singhania", "email": "karan.singhania@bharatpay.com", "phone": "9876501010", "vpa": "karan.singhania@bharatpay", "balance_paise": 14500000, "pan": "JKLMN0123Q", "aadhaar": "999988881010", "kyc": "VERIFIED"},
    {"user_code": "u_111", "name": "Meera Nair", "email": "meera.nair@bharatpay.com", "phone": "9876501011", "vpa": "meera.nair@bharatpay", "balance_paise": 2890000, "pan": "KLMNO1234R", "aadhaar": "999988881011", "kyc": "VERIFIED"},
    {"user_code": "u_112", "name": "Aditya Joshi", "email": "aditya.joshi@bharatpay.com", "phone": "9876501012", "vpa": "aditya.joshi@bharatpay", "balance_paise": 7650000, "pan": "LMNOP2345S", "aadhaar": "999988881012", "kyc": "VERIFIED"},
    {"user_code": "u_113", "name": "Pooja Hegde", "email": "pooja.hegde@bharatpay.com", "phone": "9876501013", "vpa": "pooja.hegde@bharatpay", "balance_paise": 840000, "pan": "MNOPQ3456T", "aadhaar": "999988881013", "kyc": "PENDING"},
    {"user_code": "u_114", "name": "Siddharth Malhotra", "email": "sid.malhotra@bharatpay.com", "phone": "9876501014", "vpa": "sid.malhotra@bharatpay", "balance_paise": 11200000, "pan": "NOPQR4567U", "aadhaar": "999988881014", "kyc": "VERIFIED"},
    {"user_code": "u_115", "name": "Tanvi Kulkarni", "email": "tanvi.k@bharatpay.com", "phone": "9876501015", "vpa": "tanvi.k@bharatpay", "balance_paise": 5300000, "pan": "OPQRS5678V", "aadhaar": "999988881015", "kyc": "VERIFIED"},
    {"user_code": "u_116", "name": "Amitabh Sen", "email": "amitabh.sen@bharatpay.com", "phone": "9876501016", "vpa": "amitabh.sen@bharatpay", "balance_paise": 9100000, "pan": "PQRST6789W", "aadhaar": "999988881016", "kyc": "VERIFIED"},
    {"user_code": "u_117", "name": "Roshni Roy", "email": "roshni.roy@bharatpay.com", "phone": "9876501017", "vpa": "roshni.roy@bharatpay", "balance_paise": 3950000, "pan": "QRSTU7890X", "aadhaar": "999988881017", "kyc": "VERIFIED"},
    {"user_code": "u_118", "name": "Varun Dhawan", "email": "varun.dhawan@bharatpay.com", "phone": "9876501018", "vpa": "varun.dhawan@bharatpay", "balance_paise": 8820000, "pan": "RSTUV8901Y", "aadhaar": "999988881018", "kyc": "VERIFIED"},
]

def seed_database():
    print("[BharatPay Seed] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check current user count
        current_users_count = db.query(User).count()
        if current_users_count >= 18 and db.query(Merchant).count() >= 200:
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
                created_accounts.append((user, account))

        db.commit()
        print(f"[BharatPay Seed] Successfully verified {len(created_accounts)} user accounts.")

        # Seed 220+ Verified Merchants across categories
        if db.query(Merchant).count() < 200:
            print("[BharatPay Seed] Seeding verified merchants directory...")
            categories = [
                ("Food & Dining", ["Swiggy", "Zomato", "Chai Point", "Cafe Coffee Day", "Haldirams", "Bikanervala", "Subway", "Dominos", "Burger King", "McDonalds", "KFC", "Faasos", "Behrouz Biryani", "Barbeque Nation", "Starbucks", "Blue Tokai"]),
                ("Groceries", ["Blinkit", "Zepto", "Instamart", "BigBasket", "Nature Basket", "DMart Ready", "More Retail", "Spencer Supermarket", "Reliance Fresh", "Star Bazaar", "Kisan Mandi"]),
                ("Utilities & Bills", ["Tata Power", "BSES Yamuna", "Bescom Electricity", "Adani Gas", "Indane LPG", "Bharat Gas", "Mahanagar Gas", "Airtel Broadband", "Jio Fiber", "Tata Play DTH"]),
                ("Travel & Transit", ["Uber India", "Ola Cabs", "Rapido", "MakeMyTrip", "IRCTC Rail", "Cleartrip", "Goibibo", "RedBus", "Delhi Metro DMRC", "Namma Metro", "Air India", "IndiGo"]),
                ("Shopping & Apparel", ["Flipkart", "Amazon Pay", "Myntra", "Ajio", "Nykaa", "Tata Cliq", "Croma Retail", "Reliance Digital", "Zudio", "Max Fashion", "Pantaloons", "FabIndia"]),
                ("Healthcare & Pharmacy", ["Apollo Pharmacy", "1mg Healthcare", "PharmEasy", "Netmeds", "MedPlus", "Max Healthcare", "Dr Lal PathLabs", "Metropolis Health"]),
                ("Entertainment & Gaming", ["BookMyShow", "PVR Cinemas", "INOX", "Hotstar Premium", "SonyLIV", "Zee5", "Spotify India", "Gaana Music", "Dream11", "Nazara Games"]),
                ("Education & Services", ["Urban Company", "Dunzo", "Unacademy", "PhysicsWallah", "Coursera India", "Cult Fit", "Anytime Fitness", "Lenskart", "Pepperfry", "Wakefit"])
            ]

            merchant_count = 0
            for cat_name, brand_list in categories:
                for brand in brand_list:
                    slug = brand.lower().replace(" ", "").replace("&", "")
                    merchant_count += 1
                    db.add(Merchant(
                        merchant_code=f"m_{slug}_{merchant_count:03d}",
                        business_name=f"{brand} Official",
                        vpa=f"{slug}@bharatpay",
                        category=cat_name,
                        verified=True,
                        rating=round(random.uniform(4.2, 4.9), 1)
                    ))
                    for loc in ["Bangalore", "Mumbai", "Delhi NCR"]:
                        merchant_count += 1
                        loc_slug = loc.lower().replace(" ", "")
                        db.add(Merchant(
                            merchant_code=f"m_{slug}_{loc_slug}_{merchant_count:03d}",
                            business_name=f"{brand} - {loc}",
                            vpa=f"{slug}.{loc_slug}@bharatpay",
                            category=cat_name,
                            verified=True,
                            rating=round(random.uniform(4.0, 4.8), 1)
                        ))

            db.commit()
            print(f"[BharatPay Seed] Successfully seeded {db.query(Merchant).count()} merchants.")

        # Seed 15-25 realistic historical transactions for each user
        if db.query(Transaction).count() < 100:
            print("[BharatPay Seed] Generating realistic 60-day spending history for all users...")
            merchants = db.query(Merchant).all()
            now = datetime.now(timezone.utc)

            common_spending = [
                ("Blinkit Quick Delivery", "blinkit@bharatpay", 35000, 85000),
                ("Swiggy Food Order", "swiggy@bharatpay", 42000, 110000),
                ("Zomato Dinner", "zomato@bharatpay", 55000, 140000),
                ("Uber Daily Commute", "uberindia@bharatpay", 28000, 65000),
                ("Ola City Ride", "olacabs@bharatpay", 22000, 52000),
                ("Tata Power Electricity Bill", "tatapower@bharatpay", 180000, 420000),
                ("Airtel Broadband Monthly", "airtelbroadband@bharatpay", 99900, 149900),
                ("Apollo Pharmacy Medicines", "apollopharmacy@bharatpay", 45000, 120000),
                ("BookMyShow Movie Tickets", "bookmyshow@bharatpay", 60000, 180000),
                ("Blue Tokai Coffee & Bites", "bluetokai@bharatpay", 32000, 65000),
                ("Chai Point Evening Snack", "chaipoint@bharatpay", 15000, 35000),
                ("Cult Fit Gym Pass", "cultfit@bharatpay", 149900, 199900),
                ("Zepto Quick Essentials", "zepto@bharatpay", 22000, 55000),
                ("Starbucks Reserve Brew", "starbucks@bharatpay", 45000, 85000),
                ("Flipkart Shopping", "flipkart@bharatpay", 120000, 350000),
            ]

            txn_idx = 1000
            for user, account in created_accounts:
                # 15-20 transactions per user over past 60 days
                num_txns = random.randint(15, 20)
                for _ in range(num_txns):
                    txn_idx += 1
                    days_ago = random.randint(1, 60)
                    hours_ago = random.randint(0, 23)
                    minutes_ago = random.randint(0, 59)
                    txn_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

                    # 80% merchant spending, 20% peer transfer
                    if random.random() < 0.8:
                        note, to_vpa, min_p, max_p = random.choice(common_spending)
                        amount_paise = random.randint(min_p, max_p)
                        recipient_acc_id = None
                    else:
                        # Peer transfer to another user
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
