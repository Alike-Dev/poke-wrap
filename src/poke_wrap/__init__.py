"""PokeWrap: async, typed, cache-aware Python wrapper for PokeAPI."""

from poke_wrap.endpoints import Endpoint
from poke_wrap.exceptions import (
    HydrationError,
    NetworkError,
    PokeAPIError,
    RateLimitError,
    ResourceNotFoundError,
)
from poke_wrap.models import (
    AbilitySlot,
    Generation,
    Pokemon,
    PokemonType,
    Reference,
    Stats,
)

__version__ = "0.1.0"

__all__ = [
    "AbilitySlot",
    # Client
    # "AsyncPokeAPIClient",
    # Endpoints
    "Endpoint",
    "Generation",
    "HydrationError",
    "NetworkError",
    # Exceptions
    "PokeAPIError",
    # Models
    "Pokemon",
    "PokemonType",
    "RateLimitError",
    "Reference",
    "ResourceNotFoundError",
    "Stats",
]