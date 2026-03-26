from fastapi import Cookie, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AdminUser, PortalUser, ServerAccount
from app.services.admin_auth_service import ADMIN_COOKIE_NAME, decode_admin_jwt
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


async def get_current_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_session: str = Cookie(default=None),
) -> AdminUser:
    if not admin_session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    config = request.app.state.config
    payload = decode_admin_jwt(admin_session, config.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid admin session")

    result = await db.execute(select(AdminUser).where(AdminUser.id == int(payload["sub"])))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="Admin not found or disabled")
    return admin
