# <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">PokeWrap<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">

**English** | [Español](README.es.md)

> Async, typed, cache-aware Python wrapper for [PokeAPI](https://pokeapi.co).

[![PyPI version](https://img.shields.io/pypi/v/poke-wrap.svg)](https://pypi.org/project/poke-wrap/)
[![Python versions](https://img.shields.io/pypi/pyversions/poke-wrap.svg)](https://pypi.org/project/poke-wrap/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Typed](https://img.shields.io/badge/typing-typed-blue.svg)](https://peps.python.org/pep-0561/)

PokeWrap ships **typed domain models** instead of raw dictionaries, so you write
`pokemon.stats.total` instead of `data["stats"][3]["base_stat"]`. It caches
every response locally to respect PokeAPI's fair-use policy, and hydrates
references on demand — never by surprise.

## Features

- 🚀 **Async-first**, built on [`httpx`](https://www.python-httpx.org/).
- 🧬 **Typed models** with [`Pydantic v2`](https://docs.pydantic.dev/) for full autocompletion.
- 🗂️ **Local caching** via [`hishel`](https://hishel.com/) (SQLite, RFC 9111-compliant).
- 🎯 **Controlled hydration** — resolve abilities and types only when you ask.
- 🐍 **Python 3.12+** with PEP 561 typing marker.

## Installation

```bash
pip install poke-wrap
```
Or with `uv`:
```
uv add poke-wrap
```

## Quick start
```python
import asyncio
from poke_wrap import AsyncPokeAPIClient

async def main() -> None:
    async with AsyncPokeAPIClient() as client:
        pikachu = await client.get_pokemon("pikachu")
        print(pikachu["name"], pikachu["id"])
        # pikachu 25

asyncio.run(main())
```
`get_pokemon` returns the raw JSON as a dict — same shape as PokeAPI's
response. It's a thin escape hatch for users who want full control.

## Typed domain models
For most users, the domain API is what you want:
```python
from poke_wrap import AsyncPokeAPIClient

async with AsyncPokeAPIClient() as client:
    pokemon = await client.get_pokemon_domain("pikachu")

    print(pokemon.name)             # "pikachu"
    print(pokemon.height_m)         # 0.4  (converted from decimetres)
    print(pokemon.weight_kg)        # 6.0  (converted from hectograms)
    print(pokemon.types)            # [<PokemonType.ELECTRIC: 'electric'>]
    print(pokemon.stats.total)      # 320
    print(pokemon.is_dual_type)     # False
```
Everything is typed: your editor autocompletes `pokemon.stats.attack` and
flags `pokemon.stats.attak` before you run the code.

## Hydration: pay for what you use
By default, references like abilities and types are lightweight (name + URL).
Use `get_pokemon_detailed` when you need the full payload:
```python
async with AsyncPokeAPIClient() as client:
    detailed = await client.get_pokemon_detailed("mewtwo")

    print(detailed.pokemon.name)              # "mewtwo"
    print(detailed.abilities[0].name)         # "pressure"
    print(detailed.abilities[0].effect)       # "Raises the PP usage..."
    print(detailed.types[0].name)             # <PokemonType.PSYCHIC: 'psychic'>
    print(detailed.types[0].damage_relations.double_damage_from)
    # [<PokemonType.BUG: 'bug'>, <PokemonType.GHOST: 'ghost'>]
```
You can opt out per resource:
```python
detailed = await client.get_pokemon_detailed(
    "mewtwo",
    hydrate_abilities=False,   # skip ability lookups
)
```
Hydrated results are cached twice: in-memory for the lifetime of the
client, and on disk via `hishel`. So the second call for the same Pokémon
costs zero HTTP requests.

## Caching
Every response is cached locally in SQLite by default, at
`.cache/poke-wrap/cache.db`. This is not optional politeness — PokeAPI's
fair-use policy explicitly asks clients to cache. Configure it:
```python
client = AsyncPokeAPIClient(
    cache_ttl=3600,                       # 1 hour
    cache_path="/tmp/my-poke-cache.db",   # custom location
)
```
Set cache_ttl in seconds. PokeAPI's own cache headers take precedence when
present; cache_ttl is the fallback.

## Error handling
All exceptions inherit from `PokeAPIError`:
```python
from poke_wrap import AsyncPokeAPIClient, ResourceNotFoundError, PokeAPIError

async with AsyncPokeAPIClient() as client:
    try:
        await client.get_pokemon("missingno")
    except ResourceNotFoundError as exc:
        print(f"{exc.resource_type}/{exc.resource_id} not found")
    except PokeAPIError as exc:
        print(f"PokeWrap failed: {exc}")
```

### Available exceptions:
Exception | When
----------|------
`PokeAPIError` | Base class; catch-all for any PokeWrap error.
`ResourceNotFoundError` | HTTP 404 from PokeAPI.
`RateLimitError` | HTTP 429 (includes retry_after when available).
`NetworkError` | Timeouts, DNS failures, refused connections.
`HydrationError` | A reference during hydration could not be resolved.

## Requirements
- Python 3.12 or newer.
- No authentication needed for PokeAPI.

## Development
```
git clone https://github.com/Alike-Dev/poke-wrap
cd poke-wrap
uv sync
uv run pytest
```
See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License
MIT — see [LICENSE](LICENSE).

