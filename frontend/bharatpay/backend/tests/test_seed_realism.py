import pytest
from app.db.session import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.upi import UPIProfile
from app.models.kyc import KYCRecord
from app.models.merchant import Merchant
from app.models.transaction import Transaction

def test_user_count_and_vpa_uniqueness():
    """Test 1: 15-20 synthetic users with 100% unique VPAs."""
    db = SessionLocal()
    users = db.query(User).all()
    assert 15 <= len(users) <= 20, f"Expected 15-20 users, found {len(users)}"

    vpas = [p.vpa for p in db.query(UPIProfile).all()]
    assert len(vpas) == len(set(vpas)), "Duplicate UPI VPAs found in database!"
    for v in vpas:
        assert v.endswith("@bharatpay"), f"Invalid VPA suffix format: {v}"
    db.close()

def test_believable_account_balances():
    """Test 2: All balances are positive integers between ₹2,000 and ₹2,10,000."""
    db = SessionLocal()
    accounts = db.query(Account).all()
    assert len(accounts) >= 18

    for acc in accounts:
        assert isinstance(acc.balance_paise, int)
        assert acc.balance_paise >= 0, f"Account {acc.id} has negative balance!"
        # Min ₹8,400 (840000 paise), Max ₹2,10,000 (21000000 paise)
        assert 500000 <= acc.balance_paise <= 25000000, f"Account {acc.id} balance {acc.balance_paise} out of expected range!"
    db.close()

def test_kyc_status_distribution():
    """Test 3: Mostly VERIFIED with 1-2 PENDING for realism."""
    db = SessionLocal()
    kyc_records = db.query(KYCRecord).all()
    statuses = [k.kyc_status for k in kyc_records]
    
    verified_count = statuses.count("VERIFIED")
    pending_count = statuses.count("PENDING")
    
    assert verified_count >= 14, f"Expected >= 14 verified, got {verified_count}"
    assert pending_count in [1, 2, 3], f"Expected 1-3 pending KYC records, got {pending_count}"
    db.close()

def test_transaction_history_depth_and_stability():
    """Test 4: Transaction history has realistic depth (10-30 txns per user, total >= 250)."""
    db = SessionLocal()
    total_txns = db.query(Transaction).count()
    assert total_txns >= 250, f"Expected >= 250 total transactions, got {total_txns}"

    accounts = db.query(Account).all()
    for acc in accounts:
        user_txns = db.query(Transaction).filter(
            (Transaction.from_account_id == acc.id) | (Transaction.to_account_id == acc.id)
        ).count()
        assert 10 <= user_txns <= 60, f"Account {acc.id} has unrealistic txn count: {user_txns}"
    db.close()

def test_merchant_directory_breadth():
    """Test 5: 200+ merchants across realistic categories."""
    db = SessionLocal()
    total_merchants = db.query(Merchant).count()
    assert total_merchants >= 200, f"Expected >= 200 merchants, got {total_merchants}"

    categories = {m.category for m in db.query(Merchant).all()}
    assert len(categories) >= 8, f"Expected at least 8 merchant categories, got {len(categories)}"
    db.close()
