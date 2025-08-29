from contextlib import asynccontextmanager
from uuid import UUID, uuid4
import base64
import hashlib
import hmac

import asyncio
from datetime import UTC, datetime
from typing import Any, AsyncGenerator, Generator, Self
import httpx

from dataclasses import dataclass, field

from config import EnvironmentVariables


@dataclass
class PartnerAPIClient:
    http_client: httpx.AsyncClient

    @classmethod
    @asynccontextmanager
    async def from_env(cls, env: EnvironmentVariables) -> AsyncGenerator[Self, None]:
        async with httpx.AsyncClient(
            base_url=str(env.partner_api_url),
            auth=PartnerAPIAuth(env),
        ) as client:
            yield cls(client)

    async def create_subscription(
        self, events: list[str], url: str, shared_secret: str
    ) -> UUID:

        res = await self.http_client.post(
            "/api/v1/subscriptions/",
            json={"url": url, "events": events, "shared_secret": shared_secret},
        )

        res.raise_for_status()

        data = res.json()

        return UUID(data["id"])

    async def delete_subscription(self, id: UUID) -> None:
        await self.http_client.delete(f"/api/v1/subscriptions/{id}/")

    async def trigger_webhook(self, event_type: str, payload: dict[str, Any]) -> UUID:
        event_id = uuid4()
        await self.http_client.post(
            f"/api/v1/sandbox/webhook/",
            json={
                "event_id": str(event_id),
                "timestamp": datetime.now(tz=UTC).isoformat(),
                "payload": payload,
                "event_type": event_type,
            },
        )

        return event_id


@dataclass
class PartnerAPIAuth(httpx.Auth):
    env: EnvironmentVariables
    _async_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _token: str | None = None
    _expires: datetime = field(
        default_factory=lambda: datetime.fromtimestamp(1), init=False
    )

    def has_valid_token(self, as_of: datetime | None = None) -> bool:
        as_of = as_of if as_of is not None else datetime.now(tz=UTC)

        return self._token is not None and self._expires < as_of

    async def async_get_token(self) -> str:
        async with self._async_lock:
            if not self.has_valid_token():
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        f"{self.env.partner_api_url}/api/v1/login/",
                        json={
                            "username": self.env.partner_api_username,
                            "password": self.env.partner_api_password,
                        },
                        timeout=60000,
                    )

                    res.raise_for_status()

                    login_json = res.json()

                    self._token = login_json["token"]
                    self._expires = datetime.fromisoformat(login_json["expires"])

            assert self._token
            return self._token

    def set_headers(self, request: httpx.Request, token: str) -> None:
        idempotency = str(uuid4())
        request.headers["Authorization"] = f"Bearer {token}"

        request.headers["x-jiko-idempotency"] = idempotency

        signing_bytes = (idempotency + request.url.path).encode() + request.content

        request.headers["x-jiko-signature"] = sign(
            signing_bytes,
            self.env.partner_api_shared_secret.encode(),
        )

        if self.env.partner_id:
            request.headers["x-jiko-partner-id"] = self.env.partner_id

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        token = await self.async_get_token()

        self.set_headers(request, token)

        yield request


def sign(payload: bytes, key: bytes) -> str:
    signature = hmac.new(key, payload, digestmod=hashlib.sha256).digest()

    return base64.b64encode(signature).decode()
