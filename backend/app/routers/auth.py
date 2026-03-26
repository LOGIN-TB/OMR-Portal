import logging
from datetime import datetime

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PortalUser, ServerAccount
from app.schemas import MagicLinkRequest, MagicLinkResponse, UserInfo
from app.services import auth_service, email_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request-magic-link", response_model=MagicLinkResponse)
async def request_magic_link(body: MagicLinkRequest, request: Request, db: AsyncSession = Depends(get_db)):
    config = request.app.state.config
    aggregator = request.app.state.aggregator
    email = body.email.lower().strip()

    if not await auth_service.check_rate_limit(db, email):
        return MagicLinkResponse(message="ok")

    matches = await aggregator.lookup_email(email)
    if not matches:
        return MagicLinkResponse(message="ok")

    result = await db.execute(select(PortalUser).where(PortalUser.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = PortalUser(email=email)
        db.add(user)
        await db.flush()

    for match in matches:
        result = await db.execute(
            select(ServerAccount).where(
                ServerAccount.server_id == match.server_id,
                ServerAccount.smtp_user_id == match.smtp_user_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.portal_user_id = user.id
            existing.server_name = match.server_name
            existing.username = match.username
            existing.company = match.company
            existing.mail_domain = match.mail_domain
            existing.is_active = match.is_active
            existing.last_synced = datetime.utcnow()
        else:
            db.add(ServerAccount(
                portal_user_id=user.id,
                server_id=match.server_id,
                server_name=match.server_name,
                smtp_user_id=match.smtp_user_id,
                username=match.username,
                company=match.company,
                mail_domain=match.mail_domain,
                is_active=match.is_active,
            ))
    await db.commit()

    token = await auth_service.create_magic_token(db, email)
    config_cache = request.app.state.config_cache
    await email_service.send_magic_link(config_cache, email, token, user.language)

    return MagicLinkResponse(message="ok")


@router.get("/verify")
async def verify(token: str, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    config = request.app.state.config
    email = await auth_service.verify_magic_token(db, token)
    if not email:
        response.status_code = 400
        return {"error": "Token invalid or expired"}

    result = await db.execute(select(PortalUser).where(PortalUser.email == email))
    user = result.scalar_one_or_none()
    if not user:
        response.status_code = 400
        return {"error": "User not found"}

    user.last_login = datetime.utcnow()
    await db.commit()

    accounts_count_result = await db.execute(
        select(ServerAccount).where(ServerAccount.portal_user_id == user.id)
    )
    accounts_count = len(accounts_count_result.scalars().all())

    jwt_token, expires = auth_service.create_jwt(user.id, user.email, user.language, config.jwt_secret)

    response.set_cookie(
        key="session",
        value=jwt_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/",
    )

    return {
        "id": user.id,
        "email": user.email,
        "language": user.language,
        "session_expires": expires.isoformat(),
        "accounts_count": accounts_count,
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session", path="/")
    return {"message": "ok"}


@router.get("/me", response_model=UserInfo)
async def me(request: Request, db: AsyncSession = Depends(get_db), session: str = Cookie(default=None)):
    if not session:
        return Response(status_code=401)

    config = request.app.state.config
    payload = auth_service.decode_jwt(session, config.jwt_secret)
    if not payload:
        return Response(status_code=401)

    result = await db.execute(select(PortalUser).where(PortalUser.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        return Response(status_code=401)

    accounts_result = await db.execute(
        select(ServerAccount).where(ServerAccount.portal_user_id == user.id)
    )
    accounts_count = len(accounts_result.scalars().all())

    from datetime import datetime, timezone
    expires = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    return UserInfo(
        id=user.id,
        email=user.email,
        language=user.language,
        session_expires=expires,
        accounts_count=accounts_count,
    )
