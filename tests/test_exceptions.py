"""Tests for the exceptions module."""

from poke_wrap.exceptions import (
    HydrationError,
    NetworkError,
    PokeAPIError,
    RateLimitError,
    ResourceNotFoundError,
)


def test_all_inherit_from_base() -> None:
    for exc_class in (
        ResourceNotFoundError,
        RateLimitError,
        NetworkError,
        HydrationError,
    ):
        assert issubclass(exc_class, PokeAPIError)


def test_resource_not_found_message() -> None:
    exc = ResourceNotFoundError("pokemon", "pikachu")
    assert "pokemon/pikachu" in str(exc)
    assert exc.resource_type == "pokemon"
    assert exc.resource_id == "pikachu"
    assert exc.url is None


def test_resource_not_found_with_url() -> None:
    exc = ResourceNotFoundError(
        "pokemon", "pikachu", url="https://pokeapi.co/api/v2/pokemon/pikachu/"
    )
    assert "https://pokeapi.co" in str(exc)
    assert exc.url is not None


def test_rate_limit_without_retry_after() -> None:
    exc = RateLimitError()
    assert exc.retry_after is None
    assert "rate limit" in str(exc).lower()


def test_rate_limit_with_retry_after() -> None:
    exc = RateLimitError(retry_after=30.0)
    assert exc.retry_after == 30.0
    assert "30s" in str(exc)


def test_network_error_with_url() -> None:
    exc = NetworkError("Connection timed out", url="https://pokeapi.co/api/v2/")
    assert exc.url == "https://pokeapi.co/api/v2/"
    assert "Connection timed out" in str(exc)


def test_hydration_error_with_cause() -> None:
    exc = HydrationError("https://pokeapi.co/api/v2/ability/46/", "circular reference")
    assert "ability/46" in str(exc)
    assert "circular reference" in str(exc)
