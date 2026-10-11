# <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">PokeWrap<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">

A modern, fully-typed asynchronous Python wrapper for [PokeAPI](https://pokeapi.co).

PokeWrap ships **typed domain models** instead of raw dictionaries, so you write
`pokemon.types[0]` instead of `data["types"][0]["type"]["name"]`. It separates the
API's DTOs from a clean domain layer, resolves references on demand (never by
surprise), and caches every response locally to respect PokeAPI's fair-use policy.

- 🚀 **Async-first** built on `httpx`
- 🧬 **Typed models** with `Pydantic v2` and full autocompletion
- 🗂️ **Local caching** via `hishel` (SQLite, RFC 9111)
- 🎯 **Controlled hydration** — you decide which references get resolved
- 🐍 **Python 3.12+**

> ⚠️ PokeWrap is in early development. The API may change before `1.0.0`.