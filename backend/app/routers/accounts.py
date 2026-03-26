from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.dependencies import verify_account_ownership
from app.models import ServerAccount

router = APIRouter()


@router.get("/{server_id}/{smtp_user_id}/stats")
async def get_stats(
    server_id: str,
    smtp_user_id: int,
    request: Request,
    _account: ServerAccount = Depends(verify_account_ownership),
):
    aggregator = request.app.state.aggregator
    return await aggregator.fetch_stats(server_id, smtp_user_id)


@router.get("/{server_id}/{smtp_user_id}/dns")
async def get_dns(
    server_id: str,
    smtp_user_id: int,
    request: Request,
    _account: ServerAccount = Depends(verify_account_ownership),
):
    aggregator = request.app.state.aggregator
    return await aggregator.fetch_dns(server_id, smtp_user_id)


@router.post("/{server_id}/{smtp_user_id}/reset-password")
async def reset_password(
    server_id: str,
    smtp_user_id: int,
    request: Request,
    _account: ServerAccount = Depends(verify_account_ownership),
):
    aggregator = request.app.state.aggregator
    return await aggregator.reset_password(server_id, smtp_user_id)


@router.get("/{server_id}/{smtp_user_id}/config-pdf")
async def get_config_pdf(
    server_id: str,
    smtp_user_id: int,
    request: Request,
    _account: ServerAccount = Depends(verify_account_ownership),
):
    aggregator = request.app.state.aggregator
    pdf_bytes = await aggregator.fetch_config_pdf(server_id, smtp_user_id)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=smtp-config.pdf"},
    )
