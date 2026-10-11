"""Schema for the ``/pokemon/{id or name}/`` endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from poke_wrap._schemas.common import BaseSchema, NamedAPIResourceSchema

__all__ = [
    "AbilitySlotSchema",
    "CriesSchema",
    "MoveSlotSchema",
    "PokemonSchema",
    "SpritesSchema",
    "StatSlotSchema",
    "TypeSlotSchema",
]


class AbilitySlotSchema(BaseSchema):
    """One entry of ``Pokemon.abilities``."""

    is_hidden: bool
    slot: int
    ability: NamedAPIResourceSchema


class TypeSlotSchema(BaseSchema):
    """One entry of ``Pokemon.types``."""

    slot: int
    type: NamedAPIResourceSchema


class StatSlotSchema(BaseSchema):
    """One entry of ``Pokemon.stats``."""

    base_stat: int
    effort: int
    stat: NamedAPIResourceSchema


class MoveSlotSchema(BaseSchema):
    """One entry of ``Pokemon.moves``.

    ``version_group_details`` is intentionally left as ``list[Any]``.
    It is a deeply nested structure that very few users need. If we
    model it in the future, replace the annotation; the shape is stable.
    """

    move: NamedAPIResourceSchema
    version_group_details: list[Any] = Field(default_factory=list)


class SpritesSchema(BaseSchema):
    """Sprite URLs for a Pokémon.

    Only the top-level sprite fields are modeled. The ``other`` and
    ``versions`` subtrees are enormous (and mostly used by tools that
    show historical sprites), so we skip them. If you need them, access
    them from the raw response via ``_get``.
    """

    front_default: str | None = None
    front_shiny: str | None = None
    front_female: str | None = None
    front_shiny_female: str | None = None
    back_default: str | None = None
    back_shiny: str | None = None
    back_female: str | None = None
    back_shiny_female: str | None = None


class CriesSchema(BaseSchema):
    """Cry audio URLs. Optional because older cached responses may lack it."""

    latest: str | None = None
    legacy: str | None = None


class PokemonSchema(BaseSchema):
    """The full response of ``GET /pokemon/{id or name}/``.

    Only fields relevant to the domain layer are modeled. Everything
    else (``game_indices``, ``held_items``, ``past_abilities``,
    ``past_stats``, ``past_types``, ``forms``, ``location_area_encounters``)
    is dropped by ``extra="ignore"``.

    If a user needs those fields, they should call ``client._get`` and
    work with the raw dict.
    """

    id: int
    name: str
    base_experience: int | None = None
    height: int  # decimetres, per PokeAPI convention
    weight: int  # hectograms, per PokeAPI convention
    is_default: bool
    order: int

    abilities: list[AbilitySlotSchema] = Field(default_factory=list[AbilitySlotSchema])
    types: list[TypeSlotSchema] = Field(default_factory=list[TypeSlotSchema])
    stats: list[StatSlotSchema] = Field(default_factory=list[StatSlotSchema])
    moves: list[MoveSlotSchema] = Field(default_factory=list[MoveSlotSchema])

    species: NamedAPIResourceSchema
    sprites: SpritesSchema = Field(default_factory=SpritesSchema)
    cries: CriesSchema | None = None