import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AppConfig, PortalSmtpConfig, ServerConfig
from app.models import PortalSetting, RelayServer

logger = logging.getLogger(__name__)


class ConfigCache:
    def __init__(self):
        self._servers: list[ServerConfig] = []
        self._settings: dict[str, str] = {}
        self._loaded = False

    async def load(self, db: AsyncSession):
        result = await db.execute(
            select(RelayServer).where(RelayServer.is_active == True)
        )
        self._servers = [
            ServerConfig(
                id=s.id,
                name=s.name,
                admin_url=s.admin_url.rstrip("/"),
                api_key=s.api_key,
            )
            for s in result.scalars().all()
        ]

        result = await db.execute(select(PortalSetting))
        self._settings = {s.key: s.value for s in result.scalars().all()}

        self._loaded = True
        logger.info(f"ConfigCache geladen: {len(self._servers)} Server, {len(self._settings)} Einstellungen")

    async def reload(self, db: AsyncSession):
        await self.load(db)

    @property
    def relay_servers(self) -> list[ServerConfig]:
        return self._servers

    @property
    def portal_smtp(self) -> PortalSmtpConfig | None:
        sender = self._settings.get("smtp_sender")
        if not sender:
            return None
        return PortalSmtpConfig(
            smtp_sender=sender,
            smtp_sender_name=self._settings.get("smtp_sender_name", "spamgo Portal"),
            smtp_server_id=self._settings.get("smtp_server_id", ""),
            smtp_username=self._settings.get("smtp_username", ""),
            smtp_password=self._settings.get("smtp_password", ""),
        )

    def get_setting(self, key: str, default: str = "") -> str:
        return self._settings.get(key, default)

    def get_setting_int(self, key: str, default: int = 0) -> int:
        try:
            return int(self._settings.get(key, str(default)))
        except ValueError:
            return default

    def get_setting_float(self, key: str, default: float = 0.0) -> float:
        try:
            return float(self._settings.get(key, str(default)))
        except ValueError:
            return default
