from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import NotificationPreference, PortalUser
from app.schemas import LanguageUpdate, NotificationPreferenceResponse, NotificationUpdate

router = APIRouter()

WARNING_TYPES = ["quota_warning", "quota_critical", "dns_problem", "rbl_listing", "high_bounce"]


@router.get("/notifications", response_model=list[NotificationPreferenceResponse])
async def get_notifications(
    user: PortalUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.portal_user_id == user.id)
    )
    existing = {p.warning_type: p.enabled for p in result.scalars().all()}
    return [
        NotificationPreferenceResponse(
            warning_type=wt,
            enabled=existing.get(wt, True),
        )
        for wt in WARNING_TYPES
    ]


@router.put("/notifications", response_model=NotificationPreferenceResponse)
async def update_notification(
    body: NotificationUpdate,
    user: PortalUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.portal_user_id == user.id,
            NotificationPreference.warning_type == body.warning_type,
        )
    )
    pref = result.scalar_one_or_none()
    if pref:
        pref.enabled = body.enabled
    else:
        pref = NotificationPreference(
            portal_user_id=user.id,
            warning_type=body.warning_type,
            enabled=body.enabled,
        )
        db.add(pref)
    await db.commit()
    return NotificationPreferenceResponse(warning_type=body.warning_type, enabled=body.enabled)


@router.put("/language")
async def update_language(
    body: LanguageUpdate,
    user: PortalUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.language not in ("de", "en"):
        return {"error": "Invalid language"}
    user.language = body.language
    await db.commit()
    return {"language": user.language}
