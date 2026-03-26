import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PortalUser, ServerAccount
from app.schemas import AccountOverview, DashboardOverviewResponse, ServerHealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
async def overview(
    request: Request,
    user: PortalUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    aggregator = request.app.state.aggregator

    result = await db.execute(
        select(ServerAccount).where(ServerAccount.portal_user_id == user.id)
    )
    db_accounts = result.scalars().all()

    if not db_accounts:
        return DashboardOverviewResponse(accounts=[])

    account_tuples = [(a.server_id, a.smtp_user_id) for a in db_accounts]
    stats_results = await aggregator.fetch_stats_multi(account_tuples)

    accounts = []
    for db_acc, stats_result in zip(db_accounts, stats_results):
        if isinstance(stats_result, Exception):
            logger.warning(f"Stats-Fehler fuer {db_acc.server_id}/{db_acc.smtp_user_id}: {stats_result}")
            accounts.append(AccountOverview(
                server_id=db_acc.server_id,
                server_name=db_acc.server_name,
                smtp_user_id=db_acc.smtp_user_id,
                username=db_acc.username,
                company=db_acc.company,
                mail_domain=db_acc.mail_domain,
                is_active=db_acc.is_active,
                server_error=True,
            ))
        else:
            today = stats_result.get("today", {})
            quota = stats_result.get("quota", {})
            accounts.append(AccountOverview(
                server_id=db_acc.server_id,
                server_name=db_acc.server_name,
                smtp_user_id=db_acc.smtp_user_id,
                username=db_acc.username,
                company=db_acc.company,
                mail_domain=db_acc.mail_domain,
                is_active=db_acc.is_active,
                today_sent=today.get("sent", 0),
                today_bounced=today.get("bounced", 0),
                quota_percentage=quota.get("percentage", 0),
                quota_package=quota.get("package", ""),
                quota_limit=quota.get("limit_day", 0),
                quota_used=quota.get("used_today", 0),
            ))

    return DashboardOverviewResponse(accounts=accounts)


@router.get("/servers-health", response_model=list[ServerHealthResponse])
async def servers_health(
    request: Request,
    _user: PortalUser = Depends(get_current_user),
):
    aggregator = request.app.state.aggregator
    results = await aggregator.health_check_all()
    response = []
    for server, result in zip(aggregator.servers, results):
        if isinstance(result, Exception):
            response.append(ServerHealthResponse(
                server_id=server.id,
                server_name=server.name,
                status="error",
                error=str(result),
            ))
        else:
            response.append(ServerHealthResponse(
                server_id=result.get("server_id", server.id),
                server_name=server.name,
                status=result.get("status", "unknown"),
                version=result.get("version"),
            ))
    return response
