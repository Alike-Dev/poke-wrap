# Contributing to PokeWrap

Thanks for your interest! This document covers the basics.

## Development setup

PokeWrap uses [`uv`](https://docs.astral.sh/uv/) for dependency management
and [Python 3.12+](https://www.python.org/).

```bash
git clone https://github.com/Alike-Dev/poke-wrap
cd poke-wrap
uv sync
```

This creates `.venv/` and installs all dev dependencies.

## Running tests

```bash
uv run pytest              # all tests
uv run pytest -v           # verbose
uv run pytest tests/test_models/   # a single directory
uv run pytest -k hydration # tests matching a pattern
```

## Linting and type checking

```bash
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy src tests      # type check
```

All three must pass before submitting a PR.

## Commits

PokeWrap uses [Conventional Commits](https://www.conventionalcommits.org/).
Rather than writing commit messages by hand, use:

```bash
uv run cz commit
```

This prompts for the type (`feat`, `fix`, `docs`, ...), scope and description,
and generates a well-formed message.

## Pull requests

1. Create a branch off `main`.
2. Make your changes with tests.
3. Run `uv run pytest && uv run ruff check . && uv run mypy src tests`.
4. Open a PR with a clear description of the change and the motivation.

For larger changes, please open an issue first to discuss the design.

## Architecture notes

The code is split into four layers:

- `_schemas/`: Pydantic DTOs mirroring PokeAPI's JSON shapes. Internal.
- `models/`: Public domain models. Stable API.
- `endpoints.py`: `Endpoint` enum.
- `async_client.py`: HTTP transport and hydration orchestration.

Data flows one way: `_schemas` → `models`. Never the reverse.