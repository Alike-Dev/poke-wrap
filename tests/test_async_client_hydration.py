"""Tests for the client hydration layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from poke_wrap.async_client import AsyncPokeAPIClient

BASE = "https://pokeapi.co/api/v2"


@pytest.fixture
async def client(tmp_path: Path) -> Any:
    async with AsyncPokeAPIClient(cache_path=tmp_path / "cache.db") as c:
        yield c


def _pokemon_payload() -> dict[str, Any]:
    return {
        "id": 150,
        "name": "mewtwo",
        "base_experience": 306,
        "height": 20,
        "weight": 1220,
        "is_default": True,
        "order": 245,
        "abilities": [
            {
                "is_hidden": False,
                "slot": 1,
                "ability": {
                    "name": "pressure",
                    "url": f"{BASE}/ability/46/",
                },
            },
        ],
        "types": [
            {
                "slot": 1,
                "type": {"name": "psychic", "url": f"{BASE}/type/14/"},
            }
        ],
        "stats": [
            {"base_stat": 106, "effort": 0, "stat": {"name": "hp", "url": f"{BASE}/stat/1/"}},
            {"base_stat": 110, "effort": 0, "stat": {"name": "attack", "url": f"{BASE}/stat/2/"}},
            {"base_stat": 90, "effort": 0, "stat": {"name": "defense", "url": f"{BASE}/stat/3/"}},
            {"base_stat": 154, "effort": 0, "stat": {"name": "special-attack", "url": f"{BASE}/stat/4/"}},
            {"base_stat": 90, "effort": 0, "stat": {"name": "special-defense", "url": f"{BASE}/stat/5/"}},
            {"base_stat": 130, "effort": 0, "stat": {"name": "speed", "url": f"{BASE}/stat/6/"}},
        ],
        "moves": [],
        "species": {"name": "mewtwo", "url": f"{BASE}/pokemon-species/150/"},
        "sprites": {"front_default": "https://example.com/mewtwo.png"},
    }


def _ability_payload() -> dict[str, Any]:
    return {
        "id": 46,
        "name": "pressure",
        "is_main_series": True,
        "generation": {"name": "generation-iii", "url": f"{BASE}/generation/3/"},
        "effect_entries": [
            {
                "effect": "Raises PP usage.",
                "short_effect": "Raises PP usage.",
                "language": {"name": "en", "url": f"{BASE}/language/9/"},
            }
        ],
        "names": [],
        "pokemon": [],
    }


def _type_payload() -> dict[str, Any]:
    return {
        "id": 14,
        "name": "psychic",
        "damage_relations": {
            "double_damage_from": [
                {"name": "bug", "url": f"{BASE}/type/7/"},
                {"name": "ghost", "url": f"{BASE}/type/8/"},
            ],
            "double_damage_to": [
                {"name": "fighting", "url": f"{BASE}/type/2/"},
                {"name": "poison", "url": f"{BASE}/type/4/"},
            ],
            "half_damage_from": [
                {"name": "fighting", "url": f"{BASE}/type/2/"},
                {"name": "psychic", "url": f"{BASE}/type/14/"},
            ],
            "half_damage_to": [
                {"name": "psychic", "url": f"{BASE}/type/14/"},
                {"name": "steel", "url": f"{BASE}/type/9/"},
            ],
            "no_damage_from": [],
            "no_damage_to": [{"name": "dark", "url": f"{BASE}/type/17/"}],
        },
    }


async def test_detailed_hydrates_abilities_and_types(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/mewtwo/", json=_pokemon_payload())
    httpx_mock.add_response(url=f"{BASE}/ability/46/", json=_ability_payload())
    httpx_mock.add_response(url=f"{BASE}/type/14/", json=_type_payload())

    detailed = await client.get_pokemon_detailed("mewtwo")

    assert detailed.pokemon.name == "mewtwo"
    assert detailed.abilities is not None
    assert detailed.abilities[0].name == "pressure"
    assert detailed.abilities[0].effect == "Raises PP usage."
    assert detailed.types is not None
    assert str(detailed.types[0].name) == "psychic"


async def test_detailed_skips_hydration_when_disabled(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(url=f"{BASE}/pokemon/mewtwo/", json=_pokemon_payload())

    detailed = await client.get_pokemon_detailed(
        "mewtwo", hydrate_abilities=False, hydrate_types=False
    )

    assert detailed.abilities is None
    assert detailed.types is None
    # Only one request should have been made
    assert len(httpx_mock.get_requests()) == 1


async def test_hydration_cache_avoids_duplicate_requests(
    client: AsyncPokeAPIClient, httpx_mock: HTTPXMock
) -> None:
    # Add Cache-Control so hishel serves the cached response without
    # revalidating on the second call. Without it, hishel would issue
    # another request and pytest-httpx would raise.
    cache_headers = {"Cache-Control": "max-age=3600"}

    httpx_mock.add_response(
        url=f"{BASE}/pokemon/mewtwo/",
        json=_pokemon_payload(),
        headers=cache_headers,
    )
    httpx_mock.add_response(
        url=f"{BASE}/ability/46/",
        json=_ability_payload(),
        headers=cache_headers,
    )
    httpx_mock.add_response(
        url=f"{BASE}/type/14/",
        json=_type_payload(),
        headers=cache_headers,
    )

    await client.get_pokemon_detailed("mewtwo")
    # Second call: hishel serves the Pokémon from its SQLite cache,
    # and the in-memory hydration cache serves abilities and types
    # without touching the network.
    await client.get_pokemon_detailed("mewtwo")

    # Total: 1 pokemon + 1 ability + 1 type = 3 requests
    assert len(httpx_mock.get_requests()) == 3