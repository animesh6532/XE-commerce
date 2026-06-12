"""
====================================================
JWT Handler for Xecommerce
====================================================
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status

# ====================================================
# JWT CONFIGURATION
# ====================================================

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET or SECRET_KEY environment variable is missing!")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30



# ====================================================
# CREATE ACCESS TOKEN
# ====================================================

def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
):

    to_encode = data.copy()

    if expires_delta:

        expire = datetime.utcnow() + expires_delta

    else:

        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# ====================================================
# VERIFY TOKEN
# ====================================================

def verify_token(
        token: str
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


verify_access_token = verify_token
# ====================================================
# GET CURRENT USER ID
# ====================================================

def get_current_user_id(
        token: str
):

    payload = verify_token(token)

    user_id = payload.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    return user_id


# ====================================================
# GET USER EMAIL
# ====================================================

def get_current_email(
        token: str
):

    payload = verify_token(token)

    return payload.get(
        "email"
    )


# ====================================================
# GET USER ROLE
# ====================================================

def get_current_role(
        token: str
):

    payload = verify_token(token)

    return payload.get(
        "role"
    )


# ====================================================
# ADMIN CHECK
# ====================================================

def is_admin(
        token: str
):

    role = get_current_role(
        token
    )

    return role == "admin"


# ====================================================
# SELLER CHECK
# ====================================================

def is_seller(
        token: str
):

    role = get_current_role(
        token
    )

    return role == "seller"


# ====================================================
# CUSTOMER CHECK
# ====================================================

def is_customer(
        token: str
):

    role = get_current_role(
        token
    )

    return role == "customer"


# ====================================================
# REFRESH TOKEN
# ====================================================

def refresh_access_token(
        token: str
):

    payload = verify_token(
        token
    )

    new_data = {

        "user_id":
            payload.get("user_id"),

        "email":
            payload.get("email"),

        "role":
            payload.get("role")
    }

    return create_access_token(
        new_data
    )


# ====================================================
# TOKEN INFORMATION
# ====================================================

def token_info(
        token: str
):

    payload = verify_token(
        token
    )

    return {

        "user_id":
            payload.get("user_id"),

        "email":
            payload.get("email"),

        "role":
            payload.get("role"),

        "expires":
            payload.get("exp")
    }


# ====================================================
# HEALTH CHECK
# ====================================================

def health():

    return {

        "status": "healthy",

        "service": "jwt_handler"
    }