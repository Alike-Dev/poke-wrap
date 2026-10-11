"""Tests for the shared schema building blocks."""

import pytest
from pydantic import ValidationError

from poke_wrap._schemas.common import APIResourceSchema, NamedAPIResourceSchema


def test_named_resource_from_valid_dict() -> None:
    ref = NamedAPIResourceSchema.model_validate(
        {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon/25/"}
    )
    assert ref.name == "pikachu"
    assert ref.url.endswith("/25/")


def test_api_resource_from_valid_dict() -> None:
    ref = APIResourceSchema.model_validate({"url": "https://pokeapi.co/api/v2/"})
    assert ref.url.endswith("/v2/")


def test_extra_fields_are_ignored() -> None:
    ref = NamedAPIResourceSchema.model_validate(
        {"name": "x", "url": "y", "unexpected": 42}
    )
    assert not hasattr(ref, "unexpected")


def test_missing_field_raises() -> None:
    with pytest.raises(ValidationError):
        NamedAPIResourceSchema.model_validate({"name": "pikachu"})


def test_schemas_are_frozen() -> None:
    ref = NamedAPIResourceSchema.model_validate({"name": "x", "url": "y"})
    with pytest.raises(ValidationError):
        ref.name = "other"  # type: ignore[misc]