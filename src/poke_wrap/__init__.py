"""PokeWrap: async, typed, cache-aware Python wrapper for PokeAPI.

Quick start::

    import asyncio
    from poke_wrap import AsyncPokeAPIClient

    async def main() -> None:
        async with AsyncPokeAPIClient() as client:
            pikachu = await client.get_pokemon("pikachu")
            print(pikachu["name"], pikachu["id"])

    asyncio.run(main())

For detailed Pokémon with hydrated abilities and types::

    async with AsyncPokeAPIClient() as client:
        mewtwo = await client.get_pokemon_detailed("mewtwo")
        print(mewtwo.pokemon.name, mewtwo.pokemon.stats.total)
        print(mewtwo.abilities[0].effect)
"""

from importlib.metadata import PackageNotFoundError, version

from poke_wrap.async_client import AsyncPokeAPIClient
from poke_wrap.endpoints import Endpoint
from poke_wrap.exceptions import (
    HydrationError,
    NetworkError,
    PokeAPIError,
    RateLimitError,
    ResourceNotFoundError,
)
from poke_wrap.models import (
    Ability,
    AbilitySlot,
    Generation,
    Pokemon,
    PokemonDetailed,
    PokemonType,
    Reference,
    Stats,
    TypeDamageRelations,
    TypeDetail,
)

try:
    __version__ = version("poke-wrap")
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed (e.g. running from a raw checkout without
    # `uv sync`). Fall back to a dev marker so imports still work.
    __version__ = "0.0.0-dev"


__all__ = [
    "Ability",
    "AbilitySlot",
    # Client
    "AsyncPokeAPIClient",
    # Endpoints
    "Endpoint",
    "Generation",
    "HydrationError",
    "NetworkError",
    # Exceptions
    "PokeAPIError",
    # Domain models
    "Pokemon",
    "PokemonDetailed",
    "PokemonType",
    "RateLimitError",
    "Reference",
    "ResourceNotFoundError",
    "Stats",
    "TypeDamageRelations",
    "TypeDetail",
    # Metadata
    "__version__",
]
