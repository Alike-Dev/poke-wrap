"""Tests for AsyncPokeAPIClient."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import pytest
from pytest_httpx import HTTPXMock

from poke_wrap.async_client import AsyncPokeAPIClient
from poke_wrap.endpoints import Endpoint
from poke_wrap.exceptions import (
    NetworkError,
    PokeAPIError,
    RateLimitError,
    ResourceNotFoundError,
)

BASE = "https://pokeapi.co/api/v2"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def client(tmp_path: Path) -> Any:
    """Provide a client with an isolated cache per test.

    ``tmp_path`` is a built-in pytest fixture: a fresh temporary directory
    unique to each test. Passing it as ``cache_path`` guarantees no cache
    leakage between tests (a cache hit from test A would break test B).
    """
    async with AsyncPokeAPIClient(cache_path=tmp_path / "cache.db") as c:
        yield c


# ---------------------------------------------------------------------------
# Construction and lifecycle
# ---------------------------------------------------------------------------

async def test_client_works_as_async_context_manager(tmp_path: Path) -> None:
    async with AsyncPokeAPIClient(cache_path=tmp_path / "cache.db") as c:
        assert isinstance(c, AsyncPokeAPIClient)


async def test_close_is_idempotent(tmp_path: Path) -> None:
    """Calling close() twice must not raise."""
    c = AsyncPokeAPIClient(cache_path=tmp_path / "cache.db")
    await c.close()
    await c.close()


async def test_cache_directory_is_created(tmp_path: Path) -> None:
    nested = tmp_path / "deep" / "nested" / "dir" / "cache.db"
    assert not nested.parent.exists()

    AsyncPokeAPIClient(cache_path=nested)
    assert nested.parent.exists()


# ---------------------------------------------------------------------------
# _get / get_pokemon: happy path
# ---------------------------------------------------------------------------

async def test_get_returns_parsed_json(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url=f"{BASE}/pokemon/pikachu/",
        json={"id": 25, "name": "pikachu"},
    )
    data = await client._get(Endpoint.POKEMON, "pikachu") # pyright: ignore[reportPrivateUsage]
    assert data == {"id": 25, "name": "pikachu"}


async def test_get_pokemon_with_numeric_id(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url=f"{BASE}/pokemon/25/",
        json={"id": 25, "name": "pikachu"},
    )
    data = await client.get_pokemon(25)
    assert data["id"] == 25


async def test_get_normalizes_case_and_whitespace(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    """Input '  PIKACHU  ' must resolve to /pokemon/pikachu/."""
    httpx_mock.add_response(
        url=f"{BASE}/pokemon/pikachu/",
        json={"id": 25, "name": "pikachu"},
    )
    # If the URL didn't match, pytest-httpx would raise
    await client.get_pokemon("  PIKACHU  ")


async def test_get_quotes_special_characters(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    """A space in the name must be percent-encoded, not sent raw."""
    httpx_mock.add_response(
        url=f"{BASE}/pokemon/mr%20mime/",
        json={"id": 122, "name": "mr-mime"},
    )
    await client.get_pokemon("mr mime")


async def test_user_agent_header_is_sent(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/pikachu/", json={})
    await client.get_pokemon("pikachu")

    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["user-agent"].startswith("poke-wrap/")


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------

async def test_404_raises_resource_not_found(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/missingno/", status_code=404)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await client.get_pokemon("missingno")

    exc = exc_info.value
    assert exc.resource_type == "pokemon"
    assert exc.resource_id == "missingno"
    assert exc.url == f"{BASE}/pokemon/missingno/"
    assert "missingno" in str(exc)


async def test_429_raises_rate_limit_with_retry_after(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url=f"{BASE}/pokemon/pikachu/",
        status_code=429,
        headers={"Retry-After": "30"},
    )

    with pytest.raises(RateLimitError) as exc_info:
        await client.get_pokemon("pikachu")

    assert exc_info.value.retry_after == 30.0


async def test_429_without_retry_after_header(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/pikachu/", status_code=429)

    with pytest.raises(RateLimitError) as exc_info:
        await client.get_pokemon("pikachu")

    assert exc_info.value.retry_after is None


async def test_500_raises_generic_pokeapi_error(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/pikachu/", status_code=500)

    with pytest.raises(PokeAPIError) as exc_info:
        await client.get_pokemon("pikachu")

    # Must be the generic case, not one of the specific subclasses
    assert type(exc_info.value) is PokeAPIError


# ---------------------------------------------------------------------------
# Network errors
# ---------------------------------------------------------------------------

async def test_timeout_raises_network_error(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_exception(httpx.TimeoutException("timed out"))

    with pytest.raises(NetworkError) as exc_info:
        await client.get_pokemon("pikachu")

    assert exc_info.value.url is not None


async def test_connection_error_raises_network_error(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_exception(httpx.ConnectError("connection refused"))

    with pytest.raises(NetworkError):
        await client.get_pokemon("pikachu")


# ---------------------------------------------------------------------------
# Exception chaining
# ---------------------------------------------------------------------------

async def test_status_error_chains_original_httpx_error(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/pikachu/", status_code=404)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await client.get_pokemon("pikachu")

    assert isinstance(exc_info.value.__cause__, httpx.HTTPStatusError)


async def test_request_error_chains_original_httpx_error(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_exception(httpx.ConnectError("nope"))

    with pytest.raises(NetworkError) as exc_info:
        await client.get_pokemon("pikachu")

    assert isinstance(exc_info.value.__cause__, httpx.RequestError)