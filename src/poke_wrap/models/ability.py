"""Domain models for the ``ability`` resource."""

from pydantic import BaseModel, ConfigDict

from poke_wrap.models.common import Generation

__all__ = ["Ability"]


class Ability(BaseModel):
    """A fully-hydrated ability.

    Unlike the lightweight ``AbilitySlot`` embedded in ``Pokemon``,
    this model contains the ability's own metadata: what it does, what
    generation it belongs to, and whether it appears in the main series.

    ``effect`` and ``short_effect`` are extracted from the English entry
    of PokeAPI's ``effect_entries``. If no English entry exists, both
    are ``None``.
    """

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    generation: Generation
    is_main_series: bool
    effect: str | None = None
    short_effect: str | None = None
