"""Tests for TypeSchema → TypeDetail conversion."""

from typing import Any

import pytest

from poke_wrap._schemas.type import TypeSchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.type import PokemonType


def _payload() -> dict[str, Any]:
    def ref(name: str) -> dict[str, str]:
        return {"name": name, "url": f"https://pokeapi.co/api/v2/type/{name}/"}

    return {
        "id": 13,
        "name": "electric",
        "damage_relations": {
            "double_damage_from": [ref("ground")],
            "double_damage_to": [ref("water"), ref("flying")],
            "half_damage_from": [ref("electric"), ref("flying"), ref("steel")],
            "half_damage_to": [ref("electric"), ref("grass"), ref("dragon")],
            "no_damage_from": [],
            "no_damage_to": [ref("ground")],
        },
    }


def test_to_domain_converts_name_to_enum() -> None:
    td = TypeSchema.model_validate(_payload()).to_domain()
    assert td.id == 13
    assert td.name == PokemonType.ELECTRIC


def test_damage_relations_are_converted() -> None:
    td = TypeSchema.model_validate(_payload()).to_domain()
    assert td.damage_relations.double_damage_from == [PokemonType.GROUND]
    assert PokemonType.WATER in td.damage_relations.double_damage_to
    assert PokemonType.FLYING in td.damage_relations.double_damage_to
    assert td.damage_relations.no_damage_to == [PokemonType.GROUND]
    assert td.damage_relations.no_damage_from == []


def test_unknown_type_in_damage_relations_raises() -> None:
    payload = _payload()
    payload["damage_relations"]["double_damage_from"] = [
        {"name": "cosmic", "url": "https://x/type/cosmic/"}
    ]
    with pytest.raises(PokeAPIError) as exc_info:
        TypeSchema.model_validate(payload).to_domain()
    assert "cosmic" in str(exc_info.value)
