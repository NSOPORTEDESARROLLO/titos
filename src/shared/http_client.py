"""
Reusable asynchronous HTTP client for communicating with external services.
Wraps httpx.AsyncClient with configurable timeouts, retries, and logging.
"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Thin wrapper around httpx.AsyncClient.

    Usage:
        client = HttpClient(base_url="https://api.example.com")
        response = await client.get("/endpoint")
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: Optional[dict] = None,
        verify: bool = True,
    ):
        """
        Initializes the HTTP client.

        Args:
            base_url: Base URL for all requests (e.g., "https://api.stripe.com").
            timeout: Default timeout in seconds for each request.
            max_retries: Number of automatic retries on transient failures.
            headers: Default headers sent with every request.
            verify: Whether to verify SSL certificates. Set to False to
                    disable certificate validation (e.g., for self-signed certs).
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout),
            headers=headers or {},
            verify=verify,
        )

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Performs a GET request."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """Performs a POST request."""
        return await self._request("POST", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """
        Internal method that executes the request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: URL path relative to base_url (e.g., "/v1/charges").

        Returns:
            httpx.Response object.

        Raises:
            httpx.HTTPError: After exhausting all retries.
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, path, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "HTTP error on %s %s (attempt %d/%d): %s",
                    method, path, attempt + 1, self.max_retries, e,
                )
                last_error = e
                if attempt < self.max_retries - 1:
                    continue
                raise
            except httpx.RequestError as e:
                logger.warning(
                    "Request error on %s %s (attempt %d/%d): %s",
                    method, path, attempt + 1, self.max_retries, e,
                )
                last_error = e
                if attempt < self.max_retries - 1:
                    continue
                raise
        raise last_error  # type: ignore[misc]

    async def close(self):
        """Closes the underlying httpx client connection."""
        await self._client.aclose()
