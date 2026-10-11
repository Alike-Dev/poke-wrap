"""Tests for Pokémon domain models."""

import pytest
from pydantic import ValidationError

from poke_wrap.models.common import Reference
from poke_wrap.models.pokemon import AbilitySlot, Pokemon, Stats
from poke_wrap.models.type import PokemonType


def _stats() -> Stats:
    return Stats(
        hp=35,
        attack=55,
        defense=40,
        special_attack=50,
        special_defense=50,
        speed=90,
    )


def test_stats_total_is_sum_of_all_fields() -> None:
    assert _stats().total == 320


def test_pokemon_construction() -> None:
    pokemon = Pokemon(
        id=25,
        name="pikachu",
        height_m=0.4,
        weight_kg=6.0,
        base_experience=112,
        is_default=True,
        order=35,
        types=[PokemonType.ELECTRIC],
        stats=_stats(),
        abilities=[
            AbilitySlot(
                ability=Reference(
                    name="static",
                    url="https://pokeapi.co/api/v2/ability/9/",
                ),
                is_hidden=False,
                slot=1,
            )
        ],
        sprite_url="https://example.com/pikachu.png",
    )
    assert pokemon.name == "pikachu"
    assert pokemon.types == [PokemonType.ELECTRIC]
    assert pokemon.abilities[0].ability.name == "static"
    assert pokemon.abilities[0].ability.resource_id == 9


def test_is_dual_type_true_for_two_types() -> None:
    pokemon = Pokemon(
        id=1,
        name="bulbasaur",
        height_m=0.7,
        weight_kg=6.9,
        base_experience=64,
        is_default=True,
        order=1,
        types=[PokemonType.GRASS, PokemonType.POISON],
        stats=_stats(),
        abilities=[],
    )
    assert pokemon.is_dual_type is True


def test_is_dual_type_false_for_single_type() -> None:
    pokemon = Pokemon(
        id=25,
        name="pikachu",
        height_m=0.4,
        weight_kg=6.0,
        base_experience=112,
        is_default=True,
        order=35,
        types=[PokemonType.ELECTRIC],
        stats=_stats(),
        abilities=[],
    )
    assert pokemon.is_dual_type is False


def test_pokemon_is_frozen() -> None:
    pokemon = Pokemon(
        id=1,
        name="bulbasaur",
        height_m=0.7,
        weight_kg=6.9,
        base_experience=64,
        is_default=True,
        order=1,
        types=[PokemonType.GRASS],
        stats=_stats(),
        abilities=[],
    )
    with pytest.raises(ValidationError):
        pokemon.name = "other"  # type: ignore[misc]


def test_types_compare_to_plain_strings() -> None:
    """PokemonType is a StrEnum, so string comparison must work."""
    pokemon = Pokemon(
        id=25,
        name="pikachu",
        height_m=0.4,
        weight_kg=6.0,
        base_experience=112,
        is_default=True,
        order=35,
        types=[PokemonType.ELECTRIC],
        stats=_stats(),
        abilities=[],
    )
    assert pokemon.types[0] == "electric"