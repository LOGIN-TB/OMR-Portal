from datetime import datetime

from pydantic import BaseModel, EmailStr


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str


class UserInfo(BaseModel):
    id: str
    email: str
    language: str
    session_expires: datetime
    accounts_count: int


class AccountOverview(BaseModel):
    server_id: str
    server_name: str
    smtp_user_id: int
    username: str
    company: str | None
    mail_domain: str | None
    is_active: bool
    today_sent: int = 0
    today_bounced: int = 0
    quota_percentage: float = 0.0
    quota_package: str = ""
    quota_limit: int = 0
    quota_used: int = 0
    server_error: bool = False


class DashboardOverviewResponse(BaseModel):
    accounts: list[AccountOverview]


class ServerHealthResponse(BaseModel):
    server_id: str
    server_name: str
    status: str
    version: str | None = None
    error: str | None = None


class LanguageUpdate(BaseModel):
    language: str


class NotificationUpdate(BaseModel):
    warning_type: str
    enabled: bool


class NotificationPreferenceResponse(BaseModel):
    warning_type: str
    enabled: bool
