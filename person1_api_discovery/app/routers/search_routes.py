"""
Search Directory Router:
13. GET /api/v2/search/merchants (JWT Auth - paginated scraping target)
14. GET /api/v2/search/ifsc/{ifsc_code} (Public / NO AUTH #1)
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from person1_api_discovery.app.auth import get_current_user
from person1_api_discovery.app.seed_data import MERCHANTS_DIRECTORY, IFSC_DIRECTORY

router = APIRouter(prefix="/api/v2/search", tags=["Search"])


@router.get("/merchants")
async def search_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(None, description="Category filter"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search merchant directory with pagination (JWT Auth).
    Ideal target for Person 2's automated data scraping and high-speed harvesting detector.
    """
    items = MERCHANTS_DIRECTORY
    if category:
        items = [m for m in items if m["category"].upper() == category.upper()]

    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    data = items[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
        "merchants": data
    }


@router.get("/ifsc/{ifsc_code}")
async def lookup_ifsc_code(ifsc_code: str):
    """
    Public IFSC Code Lookup (NO AUTH #1).
    Unauthenticated public utility endpoint.
    Returns branch details, NEFT/RTGS/IMPS flags for a given IFSC code.
    """
    clean_code = ifsc_code.strip().upper()
    branch = IFSC_DIRECTORY.get(clean_code)
    if not branch:
        # Fallback response for arbitrary 11-char IFSC code lookups
        if len(clean_code) == 11:
            return {
                "ifsc_code": clean_code,
                "bank_name": "Scheduled Commercial Bank",
                "branch": f"Branch {clean_code[-4:]}",
                "city": "National Clearing Hub",
                "state": "India",
                "rtgs": True,
                "neft": True,
                "imps": True,
                "upi": True
            }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IFSC code '{ifsc_code}' not found in clearing directory"
        )
    return branch
