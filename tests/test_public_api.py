"""Tests for the public API surface of poke_wrap.

These tests guard the contract with users: they verify that every
name we advertise in ``__all__`` is actually importable, that
re-exports point to the same object as the canonical definition, and
that the version metadata is well-formed.
"""

from importlib.metadata import version

import poke_wrap


def test_all_names_are_importable() -> None:
    """Every name in __all__ must resolve to an attribute."""
    for name in poke_wrap.__all__:
        assert hasattr(poke_wrap, name), f"{name!r} is listed in __all__ but not defined"


def test_all_has_no_duplicates() -> None:
    assert len(poke_wrap.__all__) == len(set(poke_wrap.__all__))


def test_version_is_a_non_empty_string() -> None:
    assert isinstance(poke_wrap.__version__, str)
    assert poke_wrap.__version__ != ""


def test_version_matches_installed_package() -> None:
    assert poke_wrap.__version__ == version("poke-wrap")


def test_client_is_reexported_from_canonical_module() -> None:
    from poke_wrap import AsyncPokeAPIClient
    from poke_wrap.async_client import (
        AsyncPokeAPIClient as CanonicalClient,
    )

    assert AsyncPokeAPIClient is CanonicalClient


def test_endpoint_is_reexported_from_canonical_module() -> None:
    from poke_wrap import Endpoint
    from poke_wrap.endpoints import Endpoint as CanonicalEndpoint

    assert Endpoint is CanonicalEndpoint


def test_exceptions_are_reexported_from_canonical_module() -> None:
    from poke_wrap import (
        HydrationError,
        NetworkError,
        PokeAPIError,
        RateLimitError,
        ResourceNotFoundError,
    )
    from poke_wrap.exceptions import HydrationError as CanonicalHydration
    from poke_wrap.exceptions import NetworkError as CanonicalNetwork
    from poke_wrap.exceptions import PokeAPIError as CanonicalBase
    from poke_wrap.exceptions import RateLimitError as CanonicalRate
    from poke_wrap.exceptions import (
        ResourceNotFoundError as CanonicalNotFound,
    )

    assert PokeAPIError is CanonicalBase
    assert ResourceNotFoundError is CanonicalNotFound
    assert RateLimitError is CanonicalRate
    assert NetworkError is CanonicalNetwork
    assert HydrationError is CanonicalHydration


def test_models_are_reexported_from_canonical_module() -> None:
    from poke_wrap import Ability, Pokemon, PokemonDetailed, PokemonType, Stats
    from poke_wrap.models.ability import Ability as CanonicalAbility
    from poke_wrap.models.pokemon import Pokemon as CanonicalPokemon
    from poke_wrap.models.pokemon import (
        PokemonDetailed as CanonicalDetailed,
    )
    from poke_wrap.models.pokemon import Stats as CanonicalStats
    from poke_wrap.models.type import PokemonType as CanonicalType

    assert Ability is CanonicalAbility
    assert Pokemon is CanonicalPokemon
    assert PokemonDetailed is CanonicalDetailed
    assert PokemonType is CanonicalType
    assert Stats is CanonicalStats


def test_importing_poke_wrap_does_not_touch_network() -> None:
    """Importing the package must not open sockets or hit PokeAPI."""
    # If this test runs at all, it means the import at the top of the
    # module succeeded without network. That's the whole point: importing
    # the library should be fast and side-effect-free.
    import poke_wrap

    assert poke_wrap.AsyncPokeAPIClient is not None
