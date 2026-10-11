"""Asynchronous HTTP client for PokeAPI v2."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Any, NoReturn, Self
from urllib.parse import quote

import httpx
from hishel import AsyncSqliteStorage, CacheOptions, SpecificationPolicy
from hishel.httpx import AsyncCacheClient

from poke_wrap.endpoints import Endpoint
from poke_wrap.exceptions import (
    NetworkError,
    PokeAPIError,
    RateLimitError,
    ResourceNotFoundError,
)

__all__ = ["DEFAULT_USER_AGENT", "AsyncPokeAPIClient"]


DEFAULT_USER_AGENT = "poke-wrap/0.1.0"


class AsyncPokeAPIClient:
    """Asynchronous client for PokeAPI v2.

    The client is designed to be used as an async context manager::

        async with AsyncPokeAPIClient() as client:
            pikachu = await client.get_pokemon("pikachu")

    But it can also be used manually::

        client = AsyncPokeAPIClient()
        try:
            pikachu = await client.get_pokemon("pikachu")
        finally:
            await client.close()

    All responses are cached locally via ``hishel`` (SQLite storage by
    default), so repeated requests to the same endpoint are served from
    disk and PokeAPI's fair-use policy is respected automatically.
    """

    BASE_URL = "https://pokeapi.co/api/v2/"

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        user_agent: str = DEFAULT_USER_AGENT,
        cache_ttl: float = 21600.0,  # 6 hours
        cache_path: str | Path = ".cache/poke-wrap/cache.db",
    ) -> None:
        """Configure the client.

        Args:
            timeout: Per-request timeout in seconds.
            user_agent: Value sent in the ``User-Agent`` header.
            cache_ttl: Default time-to-live for cached responses, in
                seconds. Ignored if PokeAPI sends explicit cache headers.
            cache_path: Filesystem path to the SQLite cache file. Parent
                directories are created automatically.
        """
        self.timeout = timeout

        cache_file = Path(cache_path)
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        policy = SpecificationPolicy(
            cache_options=CacheOptions(
                shared=False,
                supported_methods=["GET"],
                allow_stale=False,
            )
        )
        storage = AsyncSqliteStorage(
            database_path=str(cache_file),
            default_ttl=cache_ttl,
        )

        self._client = AsyncCacheClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={"User-Agent": user_agent},
            policy=policy,
            storage=storage,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Internal transport
    # ------------------------------------------------------------------

    async def _get_raw(
        self,
        endpoint: Endpoint,
        resource_id: str | int | None = None,
    ) -> httpx.Response:
        """Perform a GET request and return the raw ``httpx.Response``.

        Args:
            endpoint: One of the :class:`~poke_wrap.endpoints.Endpoint`
                members.
            resource_id: Name or numeric ID of the resource. If ``None``,
                the listing endpoint is requested (paginated resource).

        Returns:
            The full response, with metadata intact (headers, status,
            ``hishel`` extensions, etc.).

        Raises:
            ResourceNotFoundError: On HTTP 404.
            RateLimitError: On HTTP 429.
            NetworkError: On timeouts or connection failures.
            PokeAPIError: On any other HTTP error.
        """
        url = f"{endpoint}/"
        if resource_id is not None:
            clean_id = quote(str(resource_id).lower().strip(), safe="")
            url += f"{clean_id}/"

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            self._raise_for_status(exc, endpoint, resource_id)
        except httpx.RequestError as exc:
            raise NetworkError(str(exc), url=str(exc.request.url)) from exc

    async def _get(
        self,
        endpoint: Endpoint,
        resource_id: str | int | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request and return the parsed JSON body.

        Thin wrapper around :meth:`_get_raw` that discards HTTP metadata.
        """
        response = await self._get_raw(endpoint, resource_id)

        data: dict[str, Any]
        try:
            data = response.json()
        except Exception as ex:
            raise PokeAPIError(
                f"Unexpected respose to request: {endpoint}/{resource_id}"
                ) from ex
        
        return data

    @staticmethod
    def _raise_for_status(
        exc: httpx.HTTPStatusError,
        endpoint: Endpoint,
        resource_id: str | int | None,
    ) -> NoReturn:
        """Translate an ``httpx.HTTPStatusError`` into a PokeWrap exception.

        Always raises; declared ``NoReturn`` so type checkers know that
        control flow does not continue after the call.
        """
        response = exc.response
        if response.status_code == 404:
            raise ResourceNotFoundError(
                resource_type=str(endpoint),
                resource_id=resource_id if resource_id is not None else "list",
                url=str(response.request.url),
            ) from exc
        if response.status_code == 429:
            retry_after_header = response.headers.get("Retry-After")
            retry_after = float(retry_after_header) if retry_after_header else None
            raise RateLimitError(retry_after=retry_after) from exc
        raise PokeAPIError(f"HTTP {response.status_code} from {response.request.url}") from exc

    # ------------------------------------------------------------------
    # Public methods — only one for now, more in step 5.3
    # ------------------------------------------------------------------

    async def get_pokemon(self, name_or_id: str | int) -> dict[str, Any]:
        """Fetch a Pokémon by name or ID.

        Temporary method used to validate the transport layer. It will
        eventually return a typed :class:`~poke_wrap.models.Pokemon`.
        """
        return await self._get(Endpoint.POKEMON, name_or_id)
