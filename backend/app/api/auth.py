from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schemas import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_current_user
)

router = APIRouter()


# ---------------- Register ----------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    return register_user(db, user)


# ---------------- Login ----------------
@router.post(
    "/login",
    response_model=Token
)
def login(
        user: UserLogin,
        db: Session = Depends(get_db)
):
    token = authenticate_user(db, user)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return token


# ---------------- Current User ----------------
@router.get(
    "/me",
    response_model=UserResponse
)
def get_profile(
        current_user=Depends(get_current_user)
):
    return current_user


# ---------------- Logout ----------------
@router.post("/logout")
def logout():
    return {
        "success": True,
        "message": "Logged out successfully"
    }


# ---------------- Verify Token ----------------
@router.get("/verify-token")
def verify_token(
        current_user=Depends(get_current_user)
):
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


# ---------------- Admin Dashboard ----------------
@router.get("/admin")
def admin_route(
        current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return {
        "message": "Welcome Admin"
    }


# ---------------- Seller Dashboard ----------------
@router.get("/seller")
def seller_route(
        current_user=Depends(get_current_user)
):
    if current_user.role not in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return {
        "message": "Welcome Seller"
    }