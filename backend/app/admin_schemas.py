from datetime import datetime

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    username: str
    expires: datetime


class AdminMeResponse(BaseModel):
    id: int
    username: str


class RelayServerCreate(BaseModel):
    id: str
    name: str
    admin_url: str
    api_key: str


class RelayServerUpdate(BaseModel):
    name: str | None = None
    admin_url: str | None = None
    api_key: str | None = None
    is_active: bool | None = None


class RelayServerResponse(BaseModel):
    id: str
    name: str
    admin_url: str
    api_key_masked: str
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None


class PortalSettingsUpdate(BaseModel):
    settings: dict[str, str]


class PortalUserListItem(BaseModel):
    id: str
    email: str
    language: str
    created_at: datetime | None
    last_login: datetime | None
    accounts_count: int


class PortalUserDetail(PortalUserListItem):
    accounts: list[dict]


class AdminUserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime | None
    last_login: datetime | None


class AdminUserCreate(BaseModel):
    username: str
    password: str


class AdminUserUpdate(BaseModel):
    password: str | None = None
    is_active: bool | None = None


class SystemStatsResponse(BaseModel):
    total_users: int
    total_accounts: int
    total_servers: int
    warnings_24h: int
