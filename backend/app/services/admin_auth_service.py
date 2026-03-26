from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ADMIN_JWT_LIFETIME = timedelta(hours=4)
ADMIN_COOKIE_NAME = "admin_session"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_admin_jwt(admin_id: int, username: str, secret: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + ADMIN_JWT_LIFETIME
    payload = {
        "sub": str(admin_id),
        "username": username,
        "role": "admin",
        "exp": expires,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires


def decode_admin_jwt(token: str, secret: str) -> dict | None:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get("role") != "admin":
            return None
        return payload
    except jwt.InvalidTokenError:
        return None
