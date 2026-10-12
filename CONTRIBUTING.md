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

## Helper scripts

PokeWrap ships two PowerShell scripts that wrap the day-to-day
workflow. They are optional, but they prevent the classic "CI failed
because I forgot to run `ruff format`" cycle.

### Install once

```powershell
cd poke-wrap
.\scripts\install-global.ps1
```

This copies `pw-check.ps1` and `pw-commit.ps1` to
`$env:USERPROFILE\.local\bin` and adds that folder to your user PATH.
Restart your shell once and the commands are available from any
project on your machine.

To uninstall later:

```powershell
.\scripts\install-global.ps1 -Uninstall
```

### `pw-check`

Runs the full quality pipeline in the current project:

1. `ruff format .`
2. `ruff check .`
3. `mypy src tests`
4. `pytest`

Stops at the first failure so you can fix issues one at a time.

```powershell
pw-check
```

If a required tool (`uv`, `git` or `commitizen`) is missing, install it
in one go:

```powershell
pw-check -Install
```

### `pw-commit`

Wraps the pre-commit workflow: runs `pw-check`, shows the files that
will be staged, asks for confirmation, creates a conventional commit,
and pushes to origin.

```powershell
pw-commit
```

Flags:

| Flag | Effect |
|---|---|
| `-NoPush` | Commit only, do not push. |
| `-NoAutoAdd` | Do not `git add -A`. Commit only what is already staged. |
| `-Release` | Also run `cz bump` and push tags to trigger a PyPI release. |
| `-Install` | Install missing required tools before running. |
| `-Help` | Show full help. |

The release flow becomes a single command:

```powershell
pw-commit -Release
```

That runs the gates, commits, bumps the version, and pushes both the
commit and the tag. GitHub Actions then publishes to PyPI and creates
a GitHub Release automatically.

### Required tools

The scripts check for these and can install them with `-Install`:

| Tool | Purpose | Manual install |
|---|---|---|
| `uv` | Python runner and dependency manager | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| `git` | Version control | [git-scm.com](https://git-scm.com/download/win) |
| `commitizen` | Conventional commits and version bumps | `uv tool install commitizen` |

### Manual workflow

If you prefer not to use the scripts, the equivalent commands are:

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run cz commit
git push
```

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