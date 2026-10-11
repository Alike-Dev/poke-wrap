"""Base schemas and shared building blocks for PokeAPI DTOs.

Every schema in this package corresponds 1:1 with the JSON shape
returned by PokeAPI. They are *data transfer objects*: dumb containers
whose only job is to validate the incoming JSON and provide a stable
Python surface for the converter layer to read from.

They are intentionally not exported from the package root. Users should
work with the domain models in ``poke_wrap.models`` instead.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

__all__ = ["APIResourceSchema", "NamedAPIResourceSchema"]


class BaseSchema(BaseModel):
    """Common configuration for every PokeAPI DTO.

    - ``extra="ignore"``: PokeAPI adds fields over time. New fields must
      not break deserialization of existing responses.
    - ``frozen=True``: DTOs are immutable after construction. They are
      replaced, not modified.
    - ``populate_by_name=True``: allows construction from either the
      field name or its alias, when an alias is defined.
    """

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        populate_by_name=True,
    )


class APIResourceSchema(BaseSchema):
    """The simplest reference shape: a URL pointing to a resource.

    Example:
        ``{"url": "https://pokeapi.co/api/v2/pokemon/25/"}``
    """

    url: str


class NamedAPIResourceSchema(BaseSchema):
    """A named reference: a name and a URL.

    This is the most common reference shape in PokeAPI. It appears
    everywhere a resource is linked rather than embedded: abilities,
    types, moves, species, generations, and dozens more.
    """

    name: str
    url: str