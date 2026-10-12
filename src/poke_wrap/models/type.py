"""Domain models for the ``type`` resource."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

__all__ = ["PokemonType", "TypeDamageRelations", "TypeDetail"]


class PokemonType(StrEnum):
    """The 18 elemental types in Pokémon.

    Values match PokeAPI's type names, so ``PokemonType.FIRE == "fire"``.
    """

    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"

    def __repr__(self) -> str:
        """Show the enum member as a plain quoted string in containers.

        Without this override, ``repr()`` returns
        ``<PokemonType.ELECTRIC: 'electric'>`` and lists look cluttered.
        With it, ``[PokemonType.ELECTRIC]`` prints as ``['electric']``,
        matching the behaviour users expect from a string-like enum.
        """
        return repr(self.value)

class TypeDamageRelations(BaseModel):
    """How a type interacts with other types in battle.

    Each list is the set of types that this type takes/deals double,
    half or no damage against. All lists are deduplicated and sorted
    by declaration order in ``PokemonType``.
    """

    model_config = ConfigDict(frozen=True)

    double_damage_from: list[PokemonType]
    double_damage_to: list[PokemonType]
    half_damage_from: list[PokemonType]
    half_damage_to: list[PokemonType]
    no_damage_from: list[PokemonType]
    no_damage_to: list[PokemonType]


class TypeDetail(BaseModel):
    """A fully-hydrated type with its damage relations."""

    model_config = ConfigDict(frozen=True)

    id: int
    name: PokemonType
    damage_relations: TypeDamageRelations
