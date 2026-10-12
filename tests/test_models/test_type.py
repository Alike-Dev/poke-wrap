"""Tests for PokemonType."""

from poke_wrap.models.type import PokemonType


def test_repr_shows_quoted_value() -> None:
    assert repr(PokemonType.ELECTRIC) == "'electric'"


def test_list_of_types_prints_cleanly() -> None:
    types = [PokemonType.GRASS, PokemonType.POISON]
    assert str(types) == "['grass', 'poison']"


def test_str_and_comparison_still_work() -> None:
    assert str(PokemonType.FIRE) == "fire"
    assert PokemonType.FIRE == "fire"
