"""Domain models for the ``pokemon`` resource."""

from pydantic import BaseModel, ConfigDict

from poke_wrap.models.ability import Ability
from poke_wrap.models.common import Reference
from poke_wrap.models.type import PokemonType, TypeDetail

__all__ = ["AbilitySlot", "Pokemon", "Stats"]


class Stats(BaseModel):
    """The six base stats of a Pokémon.

    Unlike the raw PokeAPI response (which is a list of slot objects),
    this model exposes each stat as a named attribute, and computes
    the Base Stat Total (BST) on demand.
    """

    model_config = ConfigDict(frozen=True)

    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

    @property
    def total(self) -> int:
        """Base Stat Total (BST): the sum of all six stats."""
        return (
            self.hp
            + self.attack
            + self.defense
            + self.special_attack
            + self.special_defense
            + self.speed
        )


class AbilitySlot(BaseModel):
    """One ability of a Pokémon, as listed on its ``/pokemon`` entry.

    The ``ability`` reference is deliberately lightweight: it carries
    only the name and URL. Fetching the full ability payload requires
    an extra call and is opt-in (see ``get_ability``).
    """

    model_config = ConfigDict(frozen=True)

    ability: Reference
    is_hidden: bool
    slot: int


class Pokemon(BaseModel):
    """A Pokémon as returned by ``GET /pokemon/{id or name}/``.

    This is the lightweight domain model. It intentionally drops fields
    that are rarely useful (``game_indices``, ``held_items``,
    ``past_abilities``, ``past_stats``, ``past_types``, ``forms``) and
    normalises the ones it keeps:

    - ``height_m`` in metres instead of PokeAPI's decimetres.
    - ``weight_kg`` in kilograms instead of PokeAPI's hectograms.
    - ``types`` as a list of :class:`PokemonType` instead of reference slots.
    - ``stats`` as a :class:`Stats` object instead of a list.
    """

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    height_m: float
    weight_kg: float
    base_experience: int | None
    is_default: bool
    order: int

    types: list[PokemonType]
    stats: Stats
    abilities: list[AbilitySlot]

    sprite_url: str | None = None

    @property
    def is_dual_type(self) -> bool:
        """Whether the Pokémon has two types instead of one."""
        return len(self.types) == 2


class PokemonDetailed(BaseModel):
    """The result of :meth:`AsyncPokeAPIClient.get_pokemon_detailed`.

    Wraps the lightweight :class:`Pokemon` together with fully-hydrated
    versions of the references requested. Fields that were not hydrated
    are ``None``.

    The hydrated lists are **index-aligned** with the corresponding
    slots in ``pokemon``: ``detailed.abilities[i]`` corresponds to
    ``detailed.pokemon.abilities[i]``.
    """

    model_config = ConfigDict(frozen=True)

    pokemon: Pokemon
    abilities: list[Ability] | None = None
    types: list[TypeDetail] | None = None
