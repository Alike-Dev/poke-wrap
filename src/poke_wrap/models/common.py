"""Shared domain models used across multiple resources."""

from enum import StrEnum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict

__all__ = ["Generation", "Reference"]


class Generation(StrEnum):
    """A Pokémon generation, from I to IX.

    Values match the ``name`` field of PokeAPI's generation references,
    so ``Generation.IV == "generation-iv"`` holds.
    """

    I = "generation-i"  # noqa: E741
    II = "generation-ii"
    III = "generation-iii"
    IV = "generation-iv"
    V = "generation-v"
    VI = "generation-vi"
    VII = "generation-vii"
    VIII = "generation-viii"
    IX = "generation-ix"


class Reference(BaseModel):
    """A pointer to another PokeAPI resource.

    PokeAPI represents cross-resource links as ``{"name": ..., "url": ...}``
    pairs. ``Reference`` parses that pair and exposes the resource ID
    separately from the URL, so users can work with ``ref.resource_id``
    without string manipulation.

    Example::

        ref = Reference(name="static", url="https://pokeapi.co/api/v2/ability/9/")
        ref.name          # "static"
        ref.resource_id   # 9
        ref.url           # the full URL
    """

    model_config = ConfigDict(frozen=True)

    name: str
    url: str

    @property
    def resource_id(self) -> int | str:
        """Extract the trailing identifier from the reference URL."""
        path = urlparse(self.url).path.rstrip("/")
        tail = path.rsplit("/", 1)[-1]
        return int(tail) if tail.isdigit() else tail
