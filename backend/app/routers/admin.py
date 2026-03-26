import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin_schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMeResponse,
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    PortalSettingsUpdate,
    PortalUserDetail,
    PortalUserListItem,
    RelayServerCreate,
    RelayServerResponse,
    RelayServerUpdate,
    SystemStatsResponse,
)
from app.database import get_db
from app.dependencies import get_current_admin
from app.models import AdminUser, PortalSetting, PortalUser, RelayServer, ServerAccount, WarningLog
from app.services.admin_auth_service import (
    ADMIN_COOKIE_NAME,
    create_admin_jwt,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _mask_api_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return key[:4] + "***" + key[-4:]


# --- Auth ---

@router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(body: AdminLoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.username == body.username))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active or not verify_password(body.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    admin.last_login = datetime.utcnow()
    await db.commit()

    config = request.app.state.config
    token, expires = create_admin_jwt(admin.id, admin.username, config.jwt_secret)

    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=4 * 3600,
        path="/",
    )
    return AdminLoginResponse(username=admin.username, expires=expires)


@router.post("/auth/logout")
async def admin_logout(response: Response):
    response.delete_cookie(ADMIN_COOKIE_NAME, path="/")
    return {"message": "ok"}


@router.get("/auth/me", response_model=AdminMeResponse)
async def admin_me(admin: AdminUser = Depends(get_current_admin)):
    return AdminMeResponse(id=admin.id, username=admin.username)


# --- Relay Servers ---

@router.get("/servers", response_model=list[RelayServerResponse])
async def list_servers(db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(RelayServer))
    return [
        RelayServerResponse(
            id=s.id, name=s.name, admin_url=s.admin_url,
            api_key_masked=_mask_api_key(s.api_key),
            is_active=s.is_active, created_at=s.created_at, updated_at=s.updated_at,
        )
        for s in result.scalars().all()
    ]


@router.post("/servers", response_model=RelayServerResponse)
async def create_server(body: RelayServerCreate, request: Request, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    existing = await db.execute(select(RelayServer).where(RelayServer.id == body.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Server ID already exists")

    server = RelayServer(id=body.id, name=body.name, admin_url=body.admin_url.rstrip("/"), api_key=body.api_key)
    db.add(server)
    await db.commit()
    await db.refresh(server)

    await request.app.state.config_cache.reload(db)

    return RelayServerResponse(
        id=server.id, name=server.name, admin_url=server.admin_url,
        api_key_masked=_mask_api_key(server.api_key),
        is_active=server.is_active, created_at=server.created_at, updated_at=server.updated_at,
    )


@router.put("/servers/{server_id}", response_model=RelayServerResponse)
async def update_server(server_id: str, body: RelayServerUpdate, request: Request, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(RelayServer).where(RelayServer.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if body.name is not None:
        server.name = body.name
    if body.admin_url is not None:
        server.admin_url = body.admin_url.rstrip("/")
    if body.api_key is not None:
        server.api_key = body.api_key
    if body.is_active is not None:
        server.is_active = body.is_active
    server.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(server)

    await request.app.state.config_cache.reload(db)

    return RelayServerResponse(
        id=server.id, name=server.name, admin_url=server.admin_url,
        api_key_masked=_mask_api_key(server.api_key),
        is_active=server.is_active, created_at=server.created_at, updated_at=server.updated_at,
    )


@router.delete("/servers/{server_id}")
async def delete_server(server_id: str, request: Request, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(RelayServer).where(RelayServer.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    accounts_result = await db.execute(
        select(func.count()).where(ServerAccount.server_id == server_id)
    )
    if accounts_result.scalar_one() > 0:
        server.is_active = False
        server.updated_at = datetime.utcnow()
    else:
        await db.delete(server)

    await db.commit()
    await request.app.state.config_cache.reload(db)
    return {"message": "ok"}


@router.post("/servers/{server_id}/test")
async def test_server(server_id: str, request: Request, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(RelayServer).where(RelayServer.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{server.admin_url.rstrip('/')}/api/portal/health",
                headers={"X-Portal-API-Key": server.api_key},
            )
            resp.raise_for_status()
            return {"status": "ok", "data": resp.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Settings ---

@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(PortalSetting))
    return {s.key: s.value for s in result.scalars().all()}


@router.put("/settings")
async def update_settings(body: PortalSettingsUpdate, request: Request, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    for key, value in body.settings.items():
        result = await db.execute(select(PortalSetting).where(PortalSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            db.add(PortalSetting(key=key, value=value))
    await db.commit()
    await request.app.state.config_cache.reload(db)
    return {"message": "ok"}


@router.post("/settings/test-smtp")
async def test_smtp(request: Request, _admin: AdminUser = Depends(get_current_admin)):
    from app.services.email_service import _send_email
    config_cache = request.app.state.config_cache
    smtp = config_cache.portal_smtp
    if not smtp:
        raise HTTPException(status_code=400, detail="SMTP not configured")
    try:
        await _send_email(config_cache, smtp.smtp_sender, "spamgo Portal SMTP Test", "<p>SMTP-Verbindung erfolgreich.</p>")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Portal Users (read-only) ---

@router.get("/users", response_model=list[PortalUserListItem])
async def list_users(search: str = "", page: int = 1, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    query = select(PortalUser)
    if search:
        query = query.where(PortalUser.email.contains(search))
    query = query.order_by(PortalUser.created_at.desc()).offset((page - 1) * 50).limit(50)
    result = await db.execute(query)
    users = result.scalars().all()

    items = []
    for user in users:
        acc_result = await db.execute(
            select(func.count()).where(ServerAccount.portal_user_id == user.id)
        )
        items.append(PortalUserListItem(
            id=user.id, email=user.email, language=user.language,
            created_at=user.created_at, last_login=user.last_login,
            accounts_count=acc_result.scalar_one(),
        ))
    return items


@router.get("/users/{user_id}", response_model=PortalUserDetail)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(PortalUser).where(PortalUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    acc_result = await db.execute(select(ServerAccount).where(ServerAccount.portal_user_id == user.id))
    accounts = [
        {"server_id": a.server_id, "server_name": a.server_name, "username": a.username,
         "smtp_user_id": a.smtp_user_id, "company": a.company, "is_active": a.is_active}
        for a in acc_result.scalars().all()
    ]
    return PortalUserDetail(
        id=user.id, email=user.email, language=user.language,
        created_at=user.created_at, last_login=user.last_login,
        accounts_count=len(accounts), accounts=accounts,
    )


# --- Admin Users ---

@router.get("/admins", response_model=list[AdminUserResponse])
async def list_admins(db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(AdminUser).order_by(AdminUser.id))
    return [
        AdminUserResponse(id=a.id, username=a.username, is_active=a.is_active,
                          created_at=a.created_at, last_login=a.last_login)
        for a in result.scalars().all()
    ]


@router.post("/admins", response_model=AdminUserResponse)
async def create_admin(body: AdminUserCreate, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    existing = await db.execute(select(AdminUser).where(AdminUser.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")

    new_admin = AdminUser(username=body.username, password_hash=hash_password(body.password))
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return AdminUserResponse(id=new_admin.id, username=new_admin.username, is_active=new_admin.is_active,
                             created_at=new_admin.created_at, last_login=new_admin.last_login)


@router.put("/admins/{admin_id}", response_model=AdminUserResponse)
async def update_admin(admin_id: int, body: AdminUserUpdate, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")

    if body.password is not None:
        target.password_hash = hash_password(body.password)
    if body.is_active is not None:
        if not body.is_active:
            active_count = await db.execute(
                select(func.count()).where(AdminUser.is_active == True, AdminUser.id != admin_id)
            )
            if active_count.scalar_one() == 0:
                raise HTTPException(status_code=400, detail="Cannot deactivate last active admin")
        target.is_active = body.is_active
    await db.commit()
    await db.refresh(target)
    return AdminUserResponse(id=target.id, username=target.username, is_active=target.is_active,
                             created_at=target.created_at, last_login=target.last_login)


@router.delete("/admins/{admin_id}")
async def delete_admin(admin_id: int, db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")

    active_count = await db.execute(
        select(func.count()).where(AdminUser.is_active == True, AdminUser.id != admin_id)
    )
    if active_count.scalar_one() == 0:
        raise HTTPException(status_code=400, detail="Cannot delete last active admin")

    await db.delete(target)
    await db.commit()
    return {"message": "ok"}


# --- System ---

@router.get("/system/health")
async def system_health(request: Request, _admin: AdminUser = Depends(get_current_admin)):
    aggregator = request.app.state.aggregator
    results = await aggregator.health_check_all()
    response = []
    for server, result in zip(aggregator.servers, results):
        if isinstance(result, Exception):
            response.append({"server_id": server.id, "name": server.name, "status": "error", "error": str(result)})
        else:
            response.append({"server_id": result.get("server_id", server.id), "name": server.name, "status": result.get("status"), "version": result.get("version")})
    return response


@router.get("/system/stats", response_model=SystemStatsResponse)
async def system_stats(db: AsyncSession = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    users_count = (await db.execute(select(func.count()).select_from(PortalUser))).scalar_one()
    accounts_count = (await db.execute(select(func.count()).select_from(ServerAccount))).scalar_one()
    servers_count = (await db.execute(select(func.count()).where(RelayServer.is_active == True))).scalar_one()

    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    warnings_count = (await db.execute(
        select(func.count()).where(WarningLog.sent_at >= one_day_ago)
    )).scalar_one()

    return SystemStatsResponse(
        total_users=users_count, total_accounts=accounts_count,
        total_servers=servers_count, warnings_24h=warnings_count,
    )
