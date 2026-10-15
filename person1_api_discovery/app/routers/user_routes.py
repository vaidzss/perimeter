"""
User Profile Router:
3. GET /api/v2/users/me (JWT Auth - returns user profile + PAN + Phone)
4. PUT /api/v2/users/me/contact (JWT Auth - updates contact info)
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from person1_api_discovery.app.auth import get_current_user
from person1_api_discovery.app.seed_data import USERS_DB

router = APIRouter(prefix="/api/v2/users", tags=["Users"])


class UpdateContactRequest(BaseModel):
    phone: Optional[str] = Field(None, json_schema_extra={"example": "+91-9876501001"})
    email: Optional[str] = Field(None, json_schema_extra={"example": "updated.user@examplebank.in"})


class UserProfileResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    pan: str
    govt_id_like: str
    upi_vpa: str
    role: str
    account_id: str


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve authenticated user's profile with PII fields (JWT Auth).
    """
    sub = current_user.get("sub")
    user = USERS_DB.get(sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User record not found"
        )
    return UserProfileResponse(**user)


@router.put("/me/contact")
async def update_contact_details(
    payload: UpdateContactRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update contact telephone and email details for current authenticated user (JWT Auth).
    """
    sub = current_user.get("sub")
    user = USERS_DB.get(sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User record not found"
        )

    if payload.phone:
        user["phone"] = payload.phone
    if payload.email:
        user["email"] = payload.email

    return {
        "status": "success",
        "message": "Contact details updated successfully",
        "user_id": sub,
        "phone": user["phone"],
        "email": user["email"]
    }
