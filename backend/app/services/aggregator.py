import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.config import ServerConfig

logger = logging.getLogger(__name__)


@dataclass
class AccountMatch:
    server_id: str
    server_name: str
    smtp_user_id: int
    username: str
    company: str | None = None
    service: str | None = None
    mail_domain: str | None = None
    is_active: bool = True


class ServerAggregator:
    def __init__(self, config_cache):
        self._config_cache = config_cache

    @property
    def servers(self) -> list[ServerConfig]:
        return self._config_cache.relay_servers

    async def lookup_email(self, email: str) -> list[AccountMatch]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [self._lookup_on_server(client, server, email) for server in self.servers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        matches = []
        for server, result in zip(self.servers, results):
            if isinstance(result, Exception):
                logger.warning(f"Server {server.name} nicht erreichbar: {result}")
                continue
            for match in result:
                matches.append(AccountMatch(
                    server_id=server.id,
                    server_name=server.name,
                    smtp_user_id=match["smtp_user_id"],
                    username=match["username"],
                    company=match.get("company"),
                    service=match.get("service"),
                    mail_domain=match.get("mail_domain"),
                    is_active=match.get("is_active", True),
                ))
        return matches

    async def _lookup_on_server(self, client: httpx.AsyncClient, server: ServerConfig, email: str) -> list[dict]:
        response = await client.get(
            f"{server.admin_url}/api/portal/lookup",
            params={"email": email},
            headers={"X-Portal-API-Key": server.api_key},
        )
        response.raise_for_status()
        return response.json()["matches"]

    async def fetch_stats(self, server_id: str, smtp_user_id: int) -> dict:
        server = self._get_server(server_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{server.admin_url}/api/portal/stats/{smtp_user_id}",
                headers={"X-Portal-API-Key": server.api_key},
            )
            response.raise_for_status()
            return response.json()

    async def fetch_dns(self, server_id: str, smtp_user_id: int) -> dict:
        server = self._get_server(server_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{server.admin_url}/api/portal/dns-check/{smtp_user_id}",
                headers={"X-Portal-API-Key": server.api_key},
            )
            response.raise_for_status()
            return response.json()

    async def reset_password(self, server_id: str, smtp_user_id: int) -> dict:
        server = self._get_server(server_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{server.admin_url}/api/portal/reset-password/{smtp_user_id}",
                headers={"X-Portal-API-Key": server.api_key},
            )
            response.raise_for_status()
            return response.json()

    async def fetch_config_pdf(self, server_id: str, smtp_user_id: int) -> bytes:
        server = self._get_server(server_id)
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{server.admin_url}/api/portal/config-pdf/{smtp_user_id}",
                headers={"X-Portal-API-Key": server.api_key},
            )
            response.raise_for_status()
            return response.content

    async def fetch_rbl_status(self, server_id: str) -> dict:
        server = self._get_server(server_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{server.admin_url}/api/portal/rbl-status",
                headers={"X-Portal-API-Key": server.api_key},
            )
            response.raise_for_status()
            return response.json()

    async def health_check_all(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [self._health_check(client, server) for server in self.servers]
            return await asyncio.gather(*tasks, return_exceptions=True)

    async def _health_check(self, client: httpx.AsyncClient, server: ServerConfig) -> dict:
        response = await client.get(
            f"{server.admin_url}/api/portal/health",
            headers={"X-Portal-API-Key": server.api_key},
        )
        response.raise_for_status()
        data = response.json()
        data["server_id"] = server.id
        return data

    async def fetch_stats_multi(self, accounts: list[tuple[str, int]]) -> list[dict | Exception]:
        """Fetch stats for multiple accounts in parallel. Returns list aligned with input."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = []
            for server_id, smtp_user_id in accounts:
                server = self._get_server(server_id)
                tasks.append(self._fetch_stats_single(client, server, smtp_user_id))
            return await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_stats_single(self, client: httpx.AsyncClient, server: ServerConfig, smtp_user_id: int) -> dict:
        response = await client.get(
            f"{server.admin_url}/api/portal/stats/{smtp_user_id}",
            headers={"X-Portal-API-Key": server.api_key},
        )
        response.raise_for_status()
        return response.json()

    def _get_server(self, server_id: str) -> ServerConfig:
        for s in self.servers:
            if s.id == server_id:
                return s
        raise ValueError(f"Server {server_id} nicht konfiguriert")
