"""Custom exceptions for PokeWrap.

All exceptions raised by PokeWrap inherit from :class:`PokeAPIError`,
so users can catch any library-specific error with a single ``except``
clause::

    try:
        pokemon = await client.get_pokemon("pikachu")
    except PokeAPIError as exc:
        logger.error("PokeWrap failed: %s", exc)

For finer control, catch specific subclasses instead::

    try:
        pokemon = await client.get_pokemon("missingno")
    except ResourceNotFoundError:
        ...
    except NetworkError:
        ...
"""

from __future__ import annotations

__all__ = [
    "HydrationError",
    "NetworkError",
    "PokeAPIError",
    "RateLimitError",
    "ResourceNotFoundError",
]


class PokeAPIError(Exception):
    """Base exception for every error raised by PokeWrap.

    Catch this class to handle any error originating from the library,
    regardless of its specific cause. More specific subclasses exist
    for cases where the user wants finer-grained handling.

    All PokeWrap exceptions support exception chaining via the standard
    ``raise ... from original`` pattern, so the original cause is
    preserved in ``__cause__`` and shown in the traceback.
    """


class ResourceNotFoundError(PokeAPIError):
    """Raised when a requested resource does not exist in PokeAPI.

    Corresponds to an HTTP 404 response. This typically means the name
    or ID passed by the user is wrong (e.g. ``"pikachu"`` misspelled,
    or an ID beyond the valid range).

    Attributes:
        resource_type: The PokeAPI resource type, e.g. ``"pokemon"``.
            Usually the value of an :class:`~poke_wrap.endpoints.Endpoint`.
        resource_id: The name or ID that was requested.
        url: The full URL that returned 404, if available.
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str | int,
        *,
        url: str | None = None,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.url = url

        message = f"Resource '{resource_type}/{resource_id}' not found in PokeAPI"
        if url is not None:
            message += f" (URL: {url})"

        super().__init__(message)


class RateLimitError(PokeAPIError):
    """Raised when PokeAPI responds with HTTP 429 Too Many Requests.

    PokeAPI does not enforce a hard rate limit today, but this exception
    exists so that if it ever does — or if a proxy/CDN in front of it
    does — PokeWrap handles it gracefully instead of raising a generic
    error.

    Attributes:
        retry_after: Number of seconds the server suggests waiting before
            retrying, parsed from the ``Retry-After`` header. ``None`` if
            the header was not present.
    """

    def __init__(
        self,
        message: str = "PokeAPI rate limit exceeded",
        *,
        retry_after: float | None = None,
    ) -> None:
        self.retry_after = retry_after

        if retry_after is not None:
            message = f"{message} (retry after {retry_after:.0f}s)"

        super().__init__(message)


class NetworkError(PokeAPIError):
    """Raised when a network-level failure prevents a request from completing.

    Covers timeouts, DNS resolution failures, refused connections, TLS
    errors, and similar conditions. The original ``httpx`` exception is
    preserved via exception chaining, so ``exc.__cause__`` holds the
    low-level error.

    Attributes:
        url: The URL that could not be reached, if known.
    """

    def __init__(self, message: str, *, url: str | None = None) -> None:
        self.url = url

        if url is not None:
            message = f"{message} (URL: {url})"

        super().__init__(message)


class HydrationError(PokeAPIError):
    """Raised when resolving a reference during hydration fails.

    Hydration replaces ``NamedAPIResource`` references with their full
    payloads by following their URLs. This exception signals that one
    of those lookups failed — either because the reference was invalid,
    the server returned an error, or a circular reference was detected.

    Attributes:
        url: The reference URL that could not be hydrated.
    """

    def __init__(self, url: str, message: str | None = None) -> None:
        self.url = url

        full_message = f"Failed to hydrate reference at {url}"
        if message is not None:
            full_message += f": {message}"

        super().__init__(full_message)
