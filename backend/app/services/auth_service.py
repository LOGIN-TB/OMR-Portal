import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AppConfig
from app.models import MagicToken

logger = logging.getLogger(__name__)

MAGIC_TOKEN_LIFETIME = timedelta(minutes=15)
JWT_LIFETIME = timedelta(days=7)
RATE_LIMIT_PER_HOUR = 3


def create_jwt(user_id: str, email: str, language: str, secret: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + JWT_LIFETIME
    payload = {
        "sub": user_id,
        "email": email,
        "language": language,
        "exp": expires,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires


def decode_jwt(token: str, secret: str) -> dict | None:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


async def check_rate_limit(db: AsyncSession, email: str) -> bool:
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count()).where(
            MagicToken.email == email,
            MagicToken.created_at >= one_hour_ago,
        )
    )
    count = result.scalar_one()
    return count < RATE_LIMIT_PER_HOUR


async def create_magic_token(db: AsyncSession, email: str) -> str:
    token = str(uuid4())
    expires_at = datetime.utcnow() + MAGIC_TOKEN_LIFETIME
    magic = MagicToken(token=token, email=email, expires_at=expires_at)
    db.add(magic)
    await db.commit()
    return token


async def verify_magic_token(db: AsyncSession, token: str) -> str | None:
    """Returns email if token is valid, None otherwise."""
    result = await db.execute(
        select(MagicToken).where(MagicToken.token == token)
    )
    magic = result.scalar_one_or_none()
    if not magic:
        return None
    if magic.used:
        return None
    if magic.expires_at < datetime.utcnow():
        return None
    magic.used = True
    await db.commit()
    return magic.email
