"""HTTP client for an institution-controlled, OpenAI-compatible Gemma server."""

from ipaddress import ip_address, ip_network
from urllib.parse import urlparse

import httpx

from backend.app.services.errors import LocalAIUnavailableError

MAX_RESPONSE_BYTES = 1024 * 1024
PRIVATE_NETWORKS = (
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("fc00::/7"),
)


def validate_local_base_url(base_url: str) -> str:
    """Reject endpoints that are not explicit loopback or private-network hosts."""
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Gemma base URL must use HTTP(S) and include a host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Gemma base URL cannot include credentials, query, or fragment")

    hostname = parsed.hostname.lower()
    if hostname != "localhost":
        try:
            address = ip_address(hostname)
        except ValueError as error:
            raise ValueError(
                "Gemma host must be localhost or an explicit private/loopback IP address"
            ) from error
        if not address.is_loopback and not any(address in network for network in PRIVATE_NETWORKS):
            raise ValueError("Gemma endpoint must remain on a private or loopback network")
    return base_url.rstrip("/")


class LocalGemmaClient:
    """Call a local Gemma chat-completions endpoint without proxy inheritance."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = f"{validate_local_base_url(base_url)}/"
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                trust_env=False,
                follow_redirects=False,
                transport=self.transport,
            ) as client:
                response = await client.post("chat/completions", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise LocalAIUnavailableError(
                "the local Gemma runtime is unavailable or returned an error"
            ) from error

        if len(response.content) > MAX_RESPONSE_BYTES:
            raise LocalAIUnavailableError("the local Gemma response exceeded the size limit")
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (IndexError, KeyError, TypeError, ValueError) as error:
            raise LocalAIUnavailableError(
                "the local Gemma runtime returned an invalid response envelope"
            ) from error
        if not isinstance(content, str) or not content.strip():
            raise LocalAIUnavailableError("the local Gemma runtime returned an empty response")
        return content
