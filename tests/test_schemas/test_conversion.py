"""Tests for DTO → domain conversion."""

from typing import Any

import pytest

from poke_wrap._schemas.common import NamedAPIResourceSchema
from poke_wrap._schemas.pokemon import PokemonSchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.common import Reference
from poke_wrap.models.type import PokemonType


def _payload() -> dict[str, Any]:
    return {
        "id": 25,
        "name": "pikachu",
        "base_experience": 112,
        "height": 4,  # decimetres → 0.4 m
        "weight": 60,  # hectograms → 6.0 kg
        "is_default": True,
        "order": 35,
        "abilities": [
            {
                "is_hidden": False,
                "slot": 1,
                "ability": {
                    "name": "static",
                    "url": "https://pokeapi.co/api/v2/ability/9/",
                },
            },
            {
                "is_hidden": True,
                "slot": 3,
                "ability": {
                    "name": "lightning-rod",
                    "url": "https://pokeapi.co/api/v2/ability/31/",
                },
            },
        ],
        "types": [
            {
                "slot": 1,
                "type": {
                    "name": "electric",
                    "url": "https://pokeapi.co/api/v2/type/13/",
                },
            }
        ],
        "stats": [
            {
                "base_stat": 35,
                "effort": 0,
                "stat": {"name": "hp", "url": "https://x/stat/1/"},
            },
            {
                "base_stat": 55,
                "effort": 0,
                "stat": {"name": "attack", "url": "https://x/stat/2/"},
            },
            {
                "base_stat": 40,
                "effort": 0,
                "stat": {"name": "defense", "url": "https://x/stat/3/"},
            },
            {
                "base_stat": 50,
                "effort": 0,
                "stat": {"name": "special-attack", "url": "https://x/stat/4/"},
            },
            {
                "base_stat": 50,
                "effort": 0,
                "stat": {"name": "special-defense", "url": "https://x/stat/5/"},
            },
            {
                "base_stat": 90,
                "effort": 0,
                "stat": {"name": "speed", "url": "https://x/stat/6/"},
            },
        ],
        "moves": [],
        "species": {
            "name": "pikachu",
            "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
        },
        "sprites": {"front_default": "https://example.com/pikachu.png"},
    }


# --- NamedAPIResourceSchema.to_domain -------------------------------------

def test_named_resource_converts_to_reference() -> None:
    schema = NamedAPIResourceSchema.model_validate(
        {"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/"}
    )
    ref = schema.to_domain()
    assert isinstance(ref, Reference)
    assert ref.name == "static"
    assert ref.resource_id == 9


# --- PokemonSchema.to_domain: happy path ----------------------------------

def test_to_domain_returns_pokemon() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert pokemon.base_experience == 112
    assert pokemon.is_default is True
    assert pokemon.order == 35


def test_height_and_weight_are_converted() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert pokemon.height_m == pytest.approx(0.4)
    assert pokemon.weight_kg == pytest.approx(6.0)


def test_types_become_pokemon_type_members() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert pokemon.types == [PokemonType.ELECTRIC]


def test_stats_are_flattened() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert pokemon.stats.hp == 35
    assert pokemon.stats.attack == 55
    assert pokemon.stats.defense == 40
    assert pokemon.stats.special_attack == 50
    assert pokemon.stats.special_defense == 50
    assert pokemon.stats.speed == 90
    assert pokemon.stats.total == 320


def test_abilities_are_converted_to_ability_slots() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert len(pokemon.abilities) == 2

    first = pokemon.abilities[0]
    assert first.ability.name == "static"
    assert first.ability.resource_id == 9
    assert first.is_hidden is False
    assert first.slot == 1

    second = pokemon.abilities[1]
    assert second.ability.name == "lightning-rod"
    assert second.is_hidden is True


def test_sprite_url_is_passed_through() -> None:
    pokemon = PokemonSchema.model_validate(_payload()).to_domain()
    assert pokemon.sprite_url == "https://example.com/pikachu.png"


def test_missing_sprite_url_becomes_none() -> None:
    payload = _payload()
    payload["sprites"] = {}
    pokemon = PokemonSchema.model_validate(payload).to_domain()
    assert pokemon.sprite_url is None


# --- Error paths ----------------------------------------------------------

def test_missing_stat_raises_pokeapi_error() -> None:
    payload = _payload()
    # Drop the speed stat
    payload["stats"] = [s for s in payload["stats"] if s["stat"]["name"] != "speed"]
    with pytest.raises(PokeAPIError) as exc_info:
        PokemonSchema.model_validate(payload).to_domain()
    assert "speed" in str(exc_info.value)
    assert "pikachu" in str(exc_info.value)


def test_unknown_type_raises_pokeapi_error() -> None:
    payload = _payload()
    payload["types"][0]["type"]["name"] = "cosmic"  # not in PokemonType
    with pytest.raises(PokeAPIError) as exc_info:
        PokemonSchema.model_validate(payload).to_domain()
    assert "cosmic" in str(exc_info.value)
    assert "pikachu" in str(exc_info.value)