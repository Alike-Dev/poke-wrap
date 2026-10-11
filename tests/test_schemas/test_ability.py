"""Tests for the AbilitySchema."""

from typing import Any

from poke_wrap._schemas.ability import AbilitySchema


def _minimal_ability_payload() -> dict[str, Any]:
    return {
        "id": 46,
        "name": "pressure",
        "is_main_series": True,
        "generation": {
            "name": "generation-iii",
            "url": "https://pokeapi.co/api/v2/generation/3/",
        },
        "effect_entries": [
            {
                "effect": "Raises the PP usage of opposing moves.",
                "short_effect": "Raises PP usage.",
                "language": {
                    "name": "en",
                    "url": "https://pokeapi.co/api/v2/language/9/",
                },
            }
        ],
        "names": [
            {
                "name": "Pressure",
                "language": {
                    "name": "en",
                    "url": "https://pokeapi.co/api/v2/language/9/",
                },
            }
        ],
        "pokemon": [
            {
                "is_hidden": False,
                "slot": 1,
                "pokemon": {
                    "name": "mewtwo",
                    "url": "https://pokeapi.co/api/v2/pokemon/150/",
                },
            }
        ],
    }


def test_parses_full_payload() -> None:
    ability = AbilitySchema.model_validate(_minimal_ability_payload())
    assert ability.id == 46
    assert ability.name == "pressure"
    assert ability.generation.name == "generation-iii"
    assert ability.effect_entries[0].language.name == "en"
    assert ability.pokemon[0].pokemon.name == "mewtwo"


def test_defaults_are_empty_lists() -> None:
    payload = _minimal_ability_payload()
    payload.pop("effect_entries")
    payload.pop("names")
    payload.pop("pokemon")
    ability = AbilitySchema.model_validate(payload)
    assert ability.effect_entries == []
    assert ability.names == []
    assert ability.pokemon == []


def test_unknown_fields_are_dropped() -> None:
    payload = _minimal_ability_payload()
    payload["flavor_text_entries"] = [{"noise": True}]
    ability = AbilitySchema.model_validate(payload)
    assert not hasattr(ability, "flavor_text_entries")
