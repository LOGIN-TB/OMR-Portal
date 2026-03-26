import os
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    id: str
    name: str
    admin_url: str
    api_key: str


@dataclass
class PortalSmtpConfig:
    smtp_sender: str
    smtp_sender_name: str
    smtp_server_id: str
    smtp_username: str
    smtp_password: str


@dataclass
class AppConfig:
    jwt_secret: str = ""
    base_url: str = "https://my.spamgo.de"
    database_url: str = "sqlite+aiosqlite:///data/portal.db"


def load_config() -> AppConfig:
    jwt_secret = os.getenv("JWT_SECRET", "")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET environment variable is required")

    return AppConfig(
        jwt_secret=jwt_secret,
        base_url=os.getenv("BASE_URL", "https://my.spamgo.de"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/portal.db"),
    )
