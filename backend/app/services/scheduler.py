import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MagicToken, NotificationPreference, PortalUser, ServerAccount, WarningLog

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler | None = None


def start_scheduler(app):
    global scheduler
    scheduler = AsyncIOScheduler(timezone="Europe/Berlin")

    scheduler.add_job(lambda: asyncio.ensure_future(_check_quotas(app)), "interval", hours=1, id="check_quotas")
    scheduler.add_job(lambda: asyncio.ensure_future(_check_dns_and_rbl(app)), "interval", hours=6, id="check_dns_rbl")
    scheduler.add_job(lambda: asyncio.ensure_future(_check_bounce_rates(app)), "cron", hour=7, id="check_bounces")
    scheduler.add_job(lambda: asyncio.ensure_future(_cleanup_tokens(app)), "cron", hour=3, id="cleanup_tokens")

    scheduler.start()
    logger.info("Scheduler gestartet")


def stop_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler gestoppt")


async def _should_send(db: AsyncSession, portal_user_id: str, warning_type: str) -> bool:
    """Check throttling (1 per type per user per 24h) and opt-out."""
    pref_result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.portal_user_id == portal_user_id,
            NotificationPreference.warning_type == warning_type,
        )
    )
    pref = pref_result.scalar_one_or_none()
    if pref and not pref.enabled:
        return False

    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    log_result = await db.execute(
        select(WarningLog).where(
            WarningLog.portal_user_id == portal_user_id,
            WarningLog.warning_type == warning_type,
            WarningLog.sent_at >= one_day_ago,
        )
    )
    if log_result.scalar_one_or_none():
        return False

    return True


async def _log_warning(db: AsyncSession, portal_user_id: str, warning_type: str, details: str = ""):
    db.add(WarningLog(portal_user_id=portal_user_id, warning_type=warning_type, details=details))
    await db.commit()


async def _check_quotas(app):
    from app.database import async_session_factory
    from app.services.email_service import send_warning

    config = app.state.config
    aggregator = app.state.aggregator

    async with async_session_factory() as db:
        result = await db.execute(
            select(ServerAccount, PortalUser).join(PortalUser, ServerAccount.portal_user_id == PortalUser.id).where(ServerAccount.is_active == True)
        )
        rows = result.all()

        account_tuples = [(row[0].server_id, row[0].smtp_user_id) for row in rows]
        if not account_tuples:
            return

        stats_results = await aggregator.fetch_stats_multi(account_tuples)

        for (account, user), stats in zip(rows, stats_results):
            if isinstance(stats, Exception):
                continue
            quota = stats.get("quota", {})
            pct = quota.get("percentage", 0)

            if pct >= 95:
                wtype = "quota_critical"
            elif pct >= 80:
                wtype = "quota_warning"
            else:
                continue

            if not await _should_send(db, user.id, wtype):
                continue

            await send_warning(config, user.email, wtype, {
                "username": account.username,
                "server_name": account.server_name,
                "percentage": f"{pct:.1f}",
                "package": quota.get("package", ""),
                "used": quota.get("used_today", 0),
                "limit": quota.get("limit_day", 0),
            }, user.language)
            await _log_warning(db, user.id, wtype, f"{pct}%")


async def _check_dns_and_rbl(app):
    from app.database import async_session_factory
    from app.services.email_service import send_warning

    config = app.state.config
    aggregator = app.state.aggregator

    async with async_session_factory() as db:
        result = await db.execute(
            select(ServerAccount, PortalUser).join(PortalUser, ServerAccount.portal_user_id == PortalUser.id).where(ServerAccount.is_active == True)
        )
        rows = result.all()

        for account, user in rows:
            try:
                dns = await aggregator.fetch_dns(account.server_id, account.smtp_user_id)
                problems = []
                for check_type in ["spf", "dkim", "dmarc"]:
                    if dns.get(check_type, {}).get("status") in ("error", "warning"):
                        problems.append(f"{check_type}: {dns[check_type].get('status')}")

                if problems and await _should_send(db, user.id, "dns_problem"):
                    await send_warning(config, user.email, "dns_problem", {
                        "username": account.username,
                        "server_name": account.server_name,
                        "domain": dns.get("domain", account.mail_domain or ""),
                        "problem": "; ".join(problems),
                    }, user.language)
                    await _log_warning(db, user.id, "dns_problem", "; ".join(problems))
            except Exception as e:
                logger.warning(f"DNS-Check fehlgeschlagen fuer {account.server_id}/{account.smtp_user_id}: {e}")

        checked_servers = set()
        for account, user in rows:
            if account.server_id in checked_servers:
                continue
            checked_servers.add(account.server_id)
            try:
                rbl = await aggregator.fetch_rbl_status(account.server_id)
                if rbl.get("status") != "clean" and rbl.get("listings"):
                    affected_result = await db.execute(
                        select(ServerAccount, PortalUser).join(PortalUser, ServerAccount.portal_user_id == PortalUser.id).where(
                            ServerAccount.server_id == account.server_id, ServerAccount.is_active == True
                        )
                    )
                    for affected_account, affected_user in affected_result.all():
                        if await _should_send(db, affected_user.id, "rbl_listing"):
                            await send_warning(config, affected_user.email, "rbl_listing", {
                                "server_name": affected_account.server_name,
                                "server_ip": rbl.get("server_ip", ""),
                                "listings": rbl.get("listings", []),
                            }, affected_user.language)
                            await _log_warning(db, affected_user.id, "rbl_listing", str(rbl.get("listings")))
            except Exception as e:
                logger.warning(f"RBL-Check fehlgeschlagen fuer {account.server_id}: {e}")


async def _check_bounce_rates(app):
    from app.database import async_session_factory
    from app.services.email_service import send_warning

    config = app.state.config
    aggregator = app.state.aggregator

    async with async_session_factory() as db:
        result = await db.execute(
            select(ServerAccount, PortalUser).join(PortalUser, ServerAccount.portal_user_id == PortalUser.id).where(ServerAccount.is_active == True)
        )
        rows = result.all()

        account_tuples = [(row[0].server_id, row[0].smtp_user_id) for row in rows]
        if not account_tuples:
            return

        stats_results = await aggregator.fetch_stats_multi(account_tuples)

        for (account, user), stats in zip(rows, stats_results):
            if isinstance(stats, Exception):
                continue
            today = stats.get("today", {})
            sent = today.get("sent", 0)
            bounced = today.get("bounced", 0)
            if sent == 0:
                continue
            bounce_rate = (bounced / sent) * 100
            if bounce_rate <= 5:
                continue
            if not await _should_send(db, user.id, "high_bounce"):
                continue

            await send_warning(config, user.email, "high_bounce", {
                "username": account.username,
                "server_name": account.server_name,
                "bounce_rate": f"{bounce_rate:.1f}",
            }, user.language)
            await _log_warning(db, user.id, "high_bounce", f"{bounce_rate:.1f}%")


async def _cleanup_tokens(app):
    from app.database import async_session_factory

    async with async_session_factory() as db:
        await db.execute(
            delete(MagicToken).where(
                (MagicToken.expires_at < datetime.utcnow()) | (MagicToken.used == True)
            )
        )
        await db.commit()
        logger.info("Abgelaufene/verwendete Tokens bereinigt")
