"""Password hashing and verification utilities."""

from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to compare against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.verify(plain_password, hashed_password)
