"""Tests for the PokemonSchema."""

from typing import Any

from poke_wrap._schemas.pokemon import PokemonSchema


def _minimal_pokemon_payload() -> dict[str, Any]:
    return {
        "id": 25,
        "name": "pikachu",
        "base_experience": 112,
        "height": 4,
        "weight": 60,
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
            }
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
                "stat": {"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"},
            }
        ],
        "moves": [],
        "species": {
            "name": "pikachu",
            "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
        },
        "sprites": {"front_default": "https://example.com/pikachu.png"},
    }


def test_parses_full_payload() -> None:
    pokemon = PokemonSchema.model_validate(_minimal_pokemon_payload())
    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert pokemon.height == 4
    assert pokemon.weight == 60
    assert pokemon.abilities[0].ability.name == "static"
    assert pokemon.types[0].type.name == "electric"
    assert pokemon.stats[0].stat.name == "hp"
    assert pokemon.species.name == "pikachu"
    assert pokemon.sprites.front_default == "https://example.com/pikachu.png"


def test_unknown_fields_are_dropped() -> None:
    payload = _minimal_pokemon_payload()
    payload["game_indices"] = [{"some": "noise"}]
    payload["held_items"] = []
    pokemon = PokemonSchema.model_validate(payload)
    assert not hasattr(pokemon, "game_indices")


def test_optional_fields_default_gracefully() -> None:
    payload = _minimal_pokemon_payload()
    payload.pop("base_experience")
    payload.pop("sprites")
    pokemon = PokemonSchema.model_validate(payload)
    assert pokemon.base_experience is None
    assert pokemon.sprites.front_default is None


def test_cries_is_optional() -> None:
    payload = _minimal_pokemon_payload()
    pokemon = PokemonSchema.model_validate(payload)
    assert pokemon.cries is None

    payload["cries"] = {
        "latest": "https://example.com/latest.ogg",
        "legacy": "https://example.com/legacy.ogg",
    }
    pokemon = PokemonSchema.model_validate(payload)
    assert pokemon.cries is not None
    assert pokemon.cries.latest == "https://example.com/latest.ogg"


def test_moves_are_not_deeply_modeled() -> None:
    payload = _minimal_pokemon_payload()
    payload["moves"] = [
        {
            "move": {"name": "thunder-shock", "url": "https://x/move/84/"},
            "version_group_details": [
                {
                    "level_learned_at": 1,
                    "version_group": {"name": "red-blue", "url": "..."},
                    "move_learn_method": {"name": "level-up", "url": "..."},
                    "order": None,
                }
            ],
        }
    ]
    pokemon = PokemonSchema.model_validate(payload)
    assert pokemon.moves[0].move.name == "thunder-shock"
    # version_group_details is list[Any], so it survives as raw dicts
    assert pokemon.moves[0].version_group_details[0]["level_learned_at"] == 1