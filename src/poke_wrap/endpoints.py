"""Enumeration of all PokeAPI v2 endpoints.

PokeAPI exposes roughly 50 top-level resources. This module collects
them into a single :class:`Endpoint` enum so that typos in endpoint
names become type errors caught at development time rather than 404s
discovered at runtime.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["Endpoint"]


class Endpoint(StrEnum):
    """Every top-level resource exposed by PokeAPI v2.

    Because ``Endpoint`` inherits from :class:`~enum.StrEnum`, members
    can be used wherever a plain string is expected::

        >>> Endpoint.POKEMON == "pokemon"
        True
        >>> f"{Endpoint.POKEMON}"
        'pokemon'

    This means you can pass an ``Endpoint`` member directly to URL
    builders or f-strings without calling ``.value``.
    """

    # --- Pokémon -----------------------------------------------------
    POKEMON = "pokemon"
    POKEMON_SPECIES = "pokemon-species"
    POKEMON_FORM = "pokemon-form"
    POKEMON_COLOR = "pokemon-color"
    POKEMON_HABITAT = "pokemon-habitat"
    POKEMON_SHAPE = "pokemon-shape"
    ABILITY = "ability"
    CHARACTERISTIC = "characteristic"
    EGG_GROUP = "egg-group"
    GENDER = "gender"
    GROWTH_RATE = "growth-rate"
    NATURE = "nature"
    POKEATHLON_STAT = "pokeathlon-stat"
    STAT = "stat"
    TYPE = "type"

    # --- Moves -------------------------------------------------------
    MOVE = "move"
    MOVE_AILMENT = "move-ailment"
    MOVE_BATTLE_STYLE = "move-battle-style"
    MOVE_CATEGORY = "move-category"
    MOVE_DAMAGE_CLASS = "move-damage-class"
    MOVE_LEARN_METHOD = "move-learn-method"
    MOVE_TARGET = "move-target"

    # --- Items -------------------------------------------------------
    ITEM = "item"
    ITEM_ATTRIBUTE = "item-attribute"
    ITEM_CATEGORY = "item-category"
    ITEM_FLING_EFFECT = "item-fling-effect"
    ITEM_POCKET = "item-pocket"

    # --- Berries -----------------------------------------------------
    BERRY = "berry"
    BERRY_FIRMNESS = "berry-firmness"
    BERRY_FLAVOR = "berry-flavor"

    # --- Evolution ---------------------------------------------------
    EVOLUTION_CHAIN = "evolution-chain"
    EVOLUTION_TRIGGER = "evolution-trigger"
    EVOLUTION_VARIABLE = "evolution-variable"

    # --- Encounters --------------------------------------------------
    ENCOUNTER_CONDITION = "encounter-condition"
    ENCOUNTER_CONDITION_VALUE = "encounter-condition-value"
    ENCOUNTER_METHOD = "encounter-method"

    # --- Locations ---------------------------------------------------
    LOCATION = "location"
    LOCATION_AREA = "location-area"
    PAL_PARK_AREA = "pal-park-area"
    REGION = "region"

    # --- Games -------------------------------------------------------
    GENERATION = "generation"
    POKEDEX = "pokedex"
    VERSION = "version"
    VERSION_GROUP = "version-group"

    # --- Contests ----------------------------------------------------
    CONTEST_EFFECT = "contest-effect"
    CONTEST_TYPE = "contest-type"
    SUPER_CONTEST_EFFECT = "super-contest-effect"

    # --- Misc --------------------------------------------------------
    CURRENCY = "currency"
    LANGUAGE = "language"
    MACHINE = "machine"
    META = "meta"

    @classmethod
    def all(cls) -> list[Endpoint]:
        """Return every endpoint as a list.

        Useful when iterating over all resources, e.g. to generate
        documentation or warm a cache::

            for endpoint in Endpoint.all():
                await client.list_resource(endpoint)
        """
        return list(cls)
