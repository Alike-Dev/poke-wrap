# Changelog

All notable changes to PokeWrap are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `AsyncPokeAPIClient` with cached HTTP transport via `httpx` and `hishel`.
- `Endpoint` StrEnum with all 51 PokeAPI v2 resources.
- Custom exception hierarchy rooted at `PokeAPIError`.
- Pydantic DTOs for `pokemon`, `ability` and `type` endpoints.
- Domain models: `Pokemon`, `PokemonDetailed`, `Stats`, `Ability`,
  `TypeDetail`, `Reference`, `Generation`, `PokemonType`.
- `get_pokemon` returning raw JSON and `get_pokemon_domain` returning typed models.
- `get_pokemon_detailed` with controlled hydration of abilities and types.
- In-memory hydration cache and SQLite response cache.
- Full public API reexport from the package root.

[Unreleased]: https://github.com/Alike-Dev/poke-wrap/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Alike-Dev/poke-wrap/releases/tag/v0.1.0