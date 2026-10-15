import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.merchant import Merchant
from app.schemas.banking import PaginatedMerchantsResponse, MerchantItem

router = APIRouter(prefix="/upi", tags=["Merchants"])

@router.get("/merchants", response_model=PaginatedMerchantsResponse)
def list_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by merchant name or category"),
    db: Session = Depends(get_db)
):
    """
    Paginated directory of verified UPI merchants.
    Supports filtering and full text searching.
    """
    query = db.query(Merchant).filter(Merchant.verified == True)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Merchant.business_name.ilike(search_term),
                Merchant.category.ilike(search_term),
                Merchant.vpa.ilike(search_term)
            )
        )

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit

    merchants = query.order_by(Merchant.id).offset(offset).limit(limit).all()

    return PaginatedMerchantsResponse(
        items=[
            MerchantItem(
                id=m.id,
                merchant_code=m.merchant_code,
                business_name=m.business_name,
                vpa=m.vpa,
                category=m.category,
                verified=m.verified,
                rating=m.rating
            )
            for m in merchants
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
