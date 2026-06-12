"""
=====================================================
Password Utility for Xecommerce
=====================================================
"""

from passlib.context import CryptContext

# =====================================================
# PASSWORD CONFIGURATION
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =====================================================
# HASH PASSWORD
# =====================================================

def hash_password(
        password: str
) -> str:
    """
    Convert plain password into hashed password.
    """

    return pwd_context.hash(
        password
    )


# =====================================================
# VERIFY PASSWORD
# =====================================================

def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    """
    Compare plain password with stored hash.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =====================================================
# PASSWORD STRENGTH CHECK
# =====================================================

def check_password_strength(
        password: str
):

    errors = []

    # Minimum length
    if len(password) < 8:

        errors.append(
            "Password must contain at least 8 characters."
        )

    # Uppercase
    if not any(
            char.isupper()
            for char in password
    ):

        errors.append(
            "Password must contain at least one uppercase letter."
        )

    # Lowercase
    if not any(
            char.islower()
            for char in password
    ):

        errors.append(
            "Password must contain at least one lowercase letter."
        )

    # Digit
    if not any(
            char.isdigit()
            for char in password
    ):

        errors.append(
            "Password must contain at least one digit."
        )

    # Special character
    special_chars = "@#$%^&*!?"

    if not any(
            char in special_chars
            for char in password
    ):

        errors.append(
            "Password must contain at least one special character."
        )

    if len(errors) == 0:

        return {

            "valid": True,

            "message": "Strong password"
        }

    return {

        "valid": False,

        "errors": errors
    }


# =====================================================
# GENERATE TEMPORARY PASSWORD
# =====================================================

def generate_temp_password():

    import random
    import string

    characters = (
            string.ascii_letters +
            string.digits +
            "@#$%"
    )

    password = "".join(
        random.choice(characters)
        for _ in range(10)
    )

    return password


# =====================================================
# PASSWORD HEALTH
# =====================================================

def health():

    return {

        "status": "healthy",

        "service": "password_utility"
    }