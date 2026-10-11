"""Tests for AbilitySchema → Ability conversion."""

from typing import Any

import pytest

from poke_wrap._schemas.ability import AbilitySchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.common import Generation


def _payload() -> dict[str, Any]:
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
                "effect": "Raises PP usage of moves targeting this Pokémon.",
                "short_effect": "Raises opposing PP usage.",
                "language": {
                    "name": "en",
                    "url": "https://pokeapi.co/api/v2/language/9/",
                },
            },
            {
                "effect": "Sube el uso de PP.",
                "short_effect": "Sube PP.",
                "language": {
                    "name": "es",
                    "url": "https://pokeapi.co/api/v2/language/7/",
                },
            },
        ],
        "names": [],
        "pokemon": [],
    }


def test_to_domain_extracts_english_effect() -> None:
    ability = AbilitySchema.model_validate(_payload()).to_domain()
    assert ability.id == 46
    assert ability.name == "pressure"
    assert ability.generation == Generation.III
    assert ability.is_main_series is True
    assert ability.effect is not None
    assert "PP usage" in ability.effect
    assert ability.short_effect == "Raises opposing PP usage."


def test_to_domain_without_english_entry() -> None:
    payload = _payload()
    payload["effect_entries"] = [
        e for e in payload["effect_entries"] if e["language"]["name"] != "en"
    ]
    ability = AbilitySchema.model_validate(payload).to_domain()
    assert ability.effect is None
    assert ability.short_effect is None


def test_unknown_generation_raises() -> None:
    payload = _payload()
    payload["generation"]["name"] = "generation-x"
    with pytest.raises(PokeAPIError) as exc_info:
        AbilitySchema.model_validate(payload).to_domain()
    assert "generation-x" in str(exc_info.value)