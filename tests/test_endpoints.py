"""Tests for the endpoints module."""

from poke_wrap.endpoints import Endpoint


def test_str_representation_is_value() -> None:
    """f-string on a member yields its raw value, not 'Endpoint.POKEMON'."""
    assert f"{Endpoint.POKEMON}" == "pokemon"
    assert f"{Endpoint.MOVE_LEARN_METHOD}" == "move-learn-method"


def test_str_comparison_with_plain_string() -> None:
    """StrEnum members compare equal to their string values."""
    assert Endpoint.POKEMON == "pokemon"
    assert Endpoint.POKEMON != "berries"


def test_all_returns_every_member() -> None:
    members = Endpoint.all()
    assert isinstance(members, list)
    assert len(members) == len(list(Endpoint))
    assert Endpoint.POKEMON in members
    assert Endpoint.VERSION_GROUP in members


def test_no_duplicate_values() -> None:
    """Each value maps to exactly one member."""
    values = [e.value for e in Endpoint]
    assert len(values) == len(set(values))


def test_all_values_are_lowercase_kebab() -> None:
    """Every value follows PokeAPI's URL convention: lowercase, hyphens."""
    for endpoint in Endpoint:
        assert endpoint.value == endpoint.value.lower()
        assert " " not in endpoint.value
        assert "_" not in endpoint.value


def test_count_is_expected() -> None:
    """Guard against accidental deletions.

    If PokeAPI adds a new endpoint, bump this number in the same commit
    that adds the member.
    """
    assert len(Endpoint) == 51
