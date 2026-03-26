from fastapi import Cookie, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PortalUser, ServerAccount
from app.services.auth_service import decode_jwt


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    session: str = Cookie(default=None),
) -> PortalUser:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    config = request.app.state.config
    payload = decode_jwt(session, config.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session")

    result = await db.execute(select(PortalUser).where(PortalUser.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def verify_account_ownership(
    server_id: str,
    smtp_user_id: int,
    user: PortalUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServerAccount:
    result = await db.execute(
        select(ServerAccount).where(
            ServerAccount.portal_user_id == user.id,
            ServerAccount.server_id == server_id,
            ServerAccount.smtp_user_id == smtp_user_id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=403, detail="Access denied")
    return account
