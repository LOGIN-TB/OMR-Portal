import json
import os
from dataclasses import dataclass, field
from pathlib import Path


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
    relay_servers: list[ServerConfig] = field(default_factory=list)
    portal_smtp: PortalSmtpConfig | None = None
    jwt_secret: str = ""
    base_url: str = "https://my.spamgo.de"
    database_url: str = "sqlite+aiosqlite:///data/portal.db"


def load_config() -> AppConfig:
    config_path = Path(os.getenv("CONFIG_PATH", "config/servers.json"))
    servers = []
    portal_smtp = None

    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)

        for s in data.get("relay_servers", []):
            servers.append(ServerConfig(
                id=s["id"],
                name=s["name"],
                admin_url=s["admin_url"].rstrip("/"),
                api_key=s["api_key"],
            ))

        portal = data.get("portal", {})
        if portal:
            portal_smtp = PortalSmtpConfig(
                smtp_sender=portal["smtp_sender"],
                smtp_sender_name=portal["smtp_sender_name"],
                smtp_server_id=portal["smtp_server_id"],
                smtp_username=portal["smtp_username"],
                smtp_password=portal["smtp_password"],
            )

    jwt_secret = os.getenv("JWT_SECRET", "")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET environment variable is required")

    return AppConfig(
        relay_servers=servers,
        portal_smtp=portal_smtp,
        jwt_secret=jwt_secret,
        base_url=os.getenv("BASE_URL", "https://my.spamgo.de"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/portal.db"),
    )
