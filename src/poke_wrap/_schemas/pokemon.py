"""Schema for the ``/pokemon/{id or name}/`` endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from poke_wrap._schemas.common import BaseSchema, NamedAPIResourceSchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.pokemon import AbilitySlot, Pokemon, Stats
from poke_wrap.models.type import PokemonType

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


    def to_domain(self) -> Pokemon:
        """Convert this DTO into the corresponding domain model.

        Handles three responsibilities:

        1. **Unit conversion**: PokeAPI returns height in decimetres and
           weight in hectograms. The domain uses metres and kilograms.
        2. **Structural flattening**: ``stats`` (a list of slots) becomes
           a :class:`~poke_wrap.models.Stats` object with named fields.
           ``types`` (a list of reference slots) becomes a list of
           :class:`~poke_wrap.models.PokemonType` members.
        3. **Reference conversion**: each nested ``NamedAPIResourceSchema``
           is turned into a domain-level ``Reference``.

        Raises:
            PokeAPIError: If the response is missing a required stat, or
                if it contains a type name that PokeWrap does not know
                about. This usually indicates either a bug in PokeWrap
                or a new addition to PokeAPI that we have not caught up
                with yet.
        """
        return Pokemon(
            id=self.id,
            name=self.name,
            height_m=self.height / 10,
            weight_kg=self.weight / 10,
            base_experience=self.base_experience,
            is_default=self.is_default,
            order=self.order,
            types=self._types_to_domain(),
            stats=self._stats_to_domain(),
            abilities=[self._ability_slot_to_domain(a) for a in self.abilities],
            sprite_url=self.sprites.front_default,
        )

    def _stats_to_domain(self) -> Stats:
        """Map the six base stats from slots into a named ``Stats`` object."""
        by_name = {slot.stat.name: slot.base_stat for slot in self.stats}
        try:
            return Stats(
                hp=by_name["hp"],
                attack=by_name["attack"],
                defense=by_name["defense"],
                special_attack=by_name["special-attack"],
                special_defense=by_name["special-defense"],
                speed=by_name["speed"],
            )
        except KeyError as exc:
            raise PokeAPIError(
                f"Pokemon {self.name!r} is missing required stat: {exc.args[0]!r}"
            ) from exc

    def _types_to_domain(self) -> list[PokemonType]:
        """Map type references into ``PokemonType`` members."""
        try:
            return [PokemonType(slot.type.name) for slot in self.types]
        except ValueError as exc:
            raise PokeAPIError(
                f"Pokemon {self.name!r} has an unknown type: {exc}"
            ) from exc

    @staticmethod
    def _ability_slot_to_domain(slot: AbilitySlotSchema) -> AbilitySlot:
        """Convert an ability slot DTO into a domain ``AbilitySlot``."""
        return AbilitySlot(
            ability=slot.ability.to_domain(),
            is_hidden=slot.is_hidden,
            slot=slot.slot,
        )