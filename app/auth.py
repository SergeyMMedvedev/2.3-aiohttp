import bcrypt


def hash_password(password: str) -> str:
    """Hash password."""
    return (bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()


def check_password(password: str, hashed_password: str) -> bool:
    """Check password."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
