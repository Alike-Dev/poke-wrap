"""Schema for the ``/ability/{id or name}/`` endpoint."""

from __future__ import annotations

from pydantic import Field

from poke_wrap._schemas.common import BaseSchema, NamedAPIResourceSchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.ability import Ability
from poke_wrap.models.common import Generation

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

    def to_domain(self) -> Ability:
        """Convert to a domain-level :class:`~poke_wrap.models.Ability`.

        English-only: ``effect`` and ``short_effect`` come from the
        ``en`` entry of ``effect_entries`` if it exists.
        """
        english = next(
            (e for e in self.effect_entries if e.language.name == "en"),
            None,
        )
        try:
            generation = Generation(self.generation.name)
        except ValueError as exc:
            raise PokeAPIError(
                f"Unknown generation for ability {self.name!r}: "
                f"{self.generation.name!r}"
            ) from exc

        return Ability(
            id=self.id,
            name=self.name,
            generation=generation,
            is_main_series=self.is_main_series,
            effect=english.effect if english else None,
            short_effect=english.short_effect if english else None,
        )