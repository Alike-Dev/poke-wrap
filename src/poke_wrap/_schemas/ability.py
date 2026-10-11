"""Schema for the ``/ability/{id or name}/`` endpoint."""

from __future__ import annotations

from pydantic import Field

from poke_wrap._schemas.common import BaseSchema, NamedAPIResourceSchema

__all__ = [
    "AbilityEffectEntrySchema",
    "AbilityNameSchema",
    "AbilityPokemonSchema",
    "AbilitySchema",
]


class AbilityEffectEntrySchema(BaseSchema):
    """One entry of ``Ability.effect_entries``."""

    effect: str
    short_effect: str
    language: NamedAPIResourceSchema


class AbilityNameSchema(BaseSchema):
    """One entry of ``Ability.names``."""

    name: str
    language: NamedAPIResourceSchema


class AbilityPokemonSchema(BaseSchema):
    """One entry of ``Ability.pokemon``. ``pokemon`` here is a reference."""

    is_hidden: bool
    slot: int
    pokemon: NamedAPIResourceSchema


class AbilitySchema(BaseSchema):
    """The full response of ``GET /ability/{id or name}/``."""

    id: int
    name: str
    is_main_series: bool
    generation: NamedAPIResourceSchema

    effect_entries: list[AbilityEffectEntrySchema] = Field(default_factory=list[AbilityEffectEntrySchema])
    names: list[AbilityNameSchema] = Field(default_factory=list[AbilityNameSchema])
    pokemon: list[AbilityPokemonSchema] = Field(default_factory=list[AbilityPokemonSchema])
    # effect_changes and flavor_text_entries are dropped for now