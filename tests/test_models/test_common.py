"""Tests for shared domain models."""

import pytest
from pydantic import ValidationError

from poke_wrap.models.common import Generation, Reference


def test_generation_values_match_pokeapi() -> None:
    assert Generation.I == "generation-i"
    assert Generation.IX == "generation-ix"


def test_reference_extracts_numeric_id() -> None:
    ref = Reference(
        name="static",
        url="https://pokeapi.co/api/v2/ability/9/",
    )
    assert ref.resource_id == 9
    assert isinstance(ref.resource_id, int)


def test_reference_handles_non_numeric_id() -> None:
    ref = Reference(
        name="pikachu",
        url="https://pokeapi.co/api/v2/pokemon/pikachu/",
    )
    assert ref.resource_id == "pikachu"


def test_reference_is_frozen() -> None:
    ref = Reference(name="x", url="https://pokeapi.co/api/v2/x/1/")
    with pytest.raises(ValidationError):
        ref.name = "other"  # type: ignore[misc]
