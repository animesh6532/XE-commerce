from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import User
from app.utils.password import (
    hash_password,
    verify_password
)
from app.utils.jwt_handler import (
    create_access_token
)

from app.notifications.email_service import EmailService
from app.monitoring.logs import (
    app_logger,
    error_logger
)


class AuthService:

    def __init__(self):

        self.email_service = EmailService()

    # ============================================
    # Register User
    # ============================================

    def register(
            self,
            db: Session,
            username: str,
            email: str,
            password: str,
            role: str = "customer"
    ):

        existing_user = db.query(
            User
        ).filter(
            User.email == email
        ).first()

        if existing_user:

            return {
                "success": False,
                "message": "Email already registered"
            }

        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=role,
            created_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        app_logger.info(
            f"New user registered: {email}"
        )

        # Welcome email
        self.email_service.send_welcome_email(
            email,
            username
        )

        return {

            "success": True,

            "message": "Registration successful",

            "user_id": user.id
        }

    # ============================================
    # Login
    # ============================================

    def login(
            self,
            db: Session,
            email: str,
            password: str
    ):

        user = db.query(
            User
        ).filter(
            User.email == email
        ).first()

        if not user:

            return {
                "success": False,
                "message": "User not found"
            }

        if not verify_password(
                password,
                user.password
        ):

            return {
                "success": False,
                "message": "Incorrect password"
            }

        token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "role": user.role
            }
        )

        app_logger.info(
            f"User login: {email}"
        )

        return {

            "success": True,

            "access_token": token,

            "token_type": "bearer",

            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }

    # ============================================
    # Get User Profile
    # ============================================

    def get_profile(
            self,
            db: Session,
            user_id: int
    ):

        user = db.query(
            User
        ).filter(
            User.id == user_id
        ).first()

        if not user:

            return {
                "success": False,
                "message": "User not found"
            }

        return user

    # ============================================
    # Change Password
    # ============================================

    def change_password(
            self,
            db: Session,
            user_id: int,
            old_password: str,
            new_password: str
    ):

        user = db.query(
            User
        ).filter(
            User.id == user_id
        ).first()

        if not user:

            return {
                "success": False,
                "message": "User not found"
            }

        if not verify_password(
                old_password,
                user.password
        ):

            return {
                "success": False,
                "message": "Old password incorrect"
            }

        user.password = hash_password(
            new_password
        )

        db.commit()

        return {

            "success": True,

            "message": "Password updated successfully"
        }

    # ============================================
    # Deactivate Account
    # ============================================

    def deactivate_account(
            self,
            db: Session,
            user_id: int
    ):

        user = db.query(
            User
        ).filter(
            User.id == user_id
        ).first()

        if not user:

            return {
                "success": False,
                "message": "User not found"
            }

        user.is_active = False

        db.commit()

        return {

            "success": True,

            "message": "Account deactivated"
        }

    # ============================================
    # Delete User
    # ============================================

    def delete_user(
            self,
            db: Session,
            user_id: int
    ):

        user = db.query(
            User
        ).filter(
            User.id == user_id
        ).first()

        if not user:

            return {
                "success": False,
                "message": "User not found"
            }

        db.delete(user)

        db.commit()

        return {

            "success": True,

            "message": "User deleted successfully"
        }

    # ============================================
    # Forgot Password
    # ============================================

    def forgot_password(
            self,
            email: str,
            reset_link: str
    ):

        self.email_service.send_password_reset(
            email,
            reset_link
        )

        return {

            "success": True,

            "message": "Password reset email sent"
        }

    # ============================================
    # Logout
    # ============================================

    def logout(self):

        return {

            "success": True,

            "message": "Logged out successfully"
        }

    # ============================================
    # Health Check
    # ============================================

    def health(self):

        return {

            "status": "healthy",

            "service": "auth_service"
        }

# Module-level wrapper functions for FastAPI routing compatibility
_auth_service = AuthService()

def register_user(db: Session, user_data):
    res = _auth_service.register(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    if not res.get("success"):
        # If user registration fails (e.g. duplicate email), raise an HTTP exception matching router expectation
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("message", "Registration failed")
        )
    # Return User model object or dict matching UserResponse schema
    return db.query(User).filter(User.id == res["user_id"]).first()

def authenticate_user(db: Session, user_data):
    res = _auth_service.login(db=db, email=user_data.email, password=user_data.password)
    if not res.get("success"):
        return None
    return {
        "access_token": res.get("access_token"),
        "token_type": res.get("token_type")
    }

from app.middleware.auth import get_current_user
