from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.utils.jwt_handler import verify_access_token

# HTTP Bearer Security Scheme
security_scheme = HTTPBearer()


# ==========================================================
# Get Current User
# ==========================================================
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
        db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        token = credentials.credentials
        payload = verify_access_token(token)

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ==========================================================
# Get Active User
# ==========================================================
def get_current_active_user(
        current_user: User = Depends(get_current_user)
):

    if not current_user.is_active:

        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )

    return current_user


# ==========================================================
# Admin Only
# ==========================================================
def admin_required(
        current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


# ==========================================================
# Seller or Admin
# ==========================================================
def seller_required(
        current_user: User = Depends(get_current_user)
):

    if current_user.role not in ["seller", "admin"]:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required"
        )

    return current_user


# ==========================================================
# Customer Only
# ==========================================================
def customer_required(
        current_user: User = Depends(get_current_user)
):

    if current_user.role != "customer":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )

    return current_user