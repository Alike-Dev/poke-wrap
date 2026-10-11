"""Schema for the ``/type/{id or name}/`` endpoint."""

from __future__ import annotations

from pydantic import Field

from poke_wrap._schemas.common import BaseSchema, NamedAPIResourceSchema
from poke_wrap.exceptions import PokeAPIError
from poke_wrap.models.type import PokemonType, TypeDamageRelations, TypeDetail

__all__ = ["TypeDamageRelationsSchema", "TypeSchema"]


class TypeDamageRelationsSchema(BaseSchema):
    """Damage relations between types."""

    double_damage_from: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])
    double_damage_to: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])
    half_damage_from: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])
    half_damage_to: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])
    no_damage_from: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])
    no_damage_to: list[NamedAPIResourceSchema] = Field(default_factory=list[NamedAPIResourceSchema])

    def to_domain(self, type_name: str) -> TypeDamageRelations:
        return TypeDamageRelations(
            double_damage_from=self._convert(self.double_damage_from, type_name),
            double_damage_to=self._convert(self.double_damage_to, type_name),
            half_damage_from=self._convert(self.half_damage_from, type_name),
            half_damage_to=self._convert(self.half_damage_to, type_name),
            no_damage_from=self._convert(self.no_damage_from, type_name),
            no_damage_to=self._convert(self.no_damage_to, type_name),
        )

    @staticmethod
    def _convert(
        refs: list[NamedAPIResourceSchema], type_name: str
    ) -> list[PokemonType]:
        try:
            return [PokemonType(r.name) for r in refs]
        except ValueError as exc:
            raise PokeAPIError(
                f"Type {type_name!r} has an unknown type in damage_relations: {exc}"
            ) from exc


class TypeSchema(BaseSchema):
    """The response of ``GET /type/{id or name}/``."""

    id: int
    name: str
    damage_relations: TypeDamageRelationsSchema

    def to_domain(self) -> TypeDetail:
        try:
            name = PokemonType(self.name)
        except ValueError as exc:
            raise PokeAPIError(f"Unknown PokemonType: {self.name!r}") from exc

        return TypeDetail(
            id=self.id,
            name=name,
            damage_relations=self.damage_relations.to_domain(self.name),
        )