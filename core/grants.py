"""Нормализация grants из YAML."""

from typing import Any

ABILITY_INCREASE = "ability_increase"


def _coerce_bool(value: Any, default: bool = True) -> bool:
    """Привести значение к bool."""
    if isinstance(value, bool):
        return value
    return default


def inherit_flags(entity: dict[str, Any]) -> tuple[bool, bool]:
    """Флаги наследования подрасы: ability_bonuses, grants."""
    inherit = entity.get("inherit")
    if isinstance(inherit, dict):
        return (
            _coerce_bool(inherit.get("ability_bonuses"), True),
            _coerce_bool(inherit.get("grants"), True),
        )
    return True, True


def grants_from_entity(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Grants сущности из ключа grants."""
    raw_grants = entity.get("grants", [])
    if not isinstance(raw_grants, list):
        return []
    return [dict(g) for g in raw_grants if isinstance(g, dict)]


def merge_entity_grants(
    parent: dict[str, Any] | None,
    entity: dict[str, Any],
    *,
    use_parent: bool,
) -> list[dict[str, Any]]:
    """Grants подрасы с учётом наследования от базовой расы."""
    _, inherit_grants = inherit_flags(entity)
    merged: list[dict[str, Any]] = []
    if use_parent and parent and inherit_grants:
        merged.extend(grants_from_entity(parent))
    merged.extend(grants_from_entity(entity))
    return merged


def grant_type(grant: dict[str, Any]) -> str:
    """Тип grant после нормализации."""
    return str(grant.get("type", ""))


def grants_of_type(
    grants: list[dict[str, Any]], type_name: str
) -> list[dict[str, Any]]:
    """Отфильтровать grants по type."""
    return [g for g in grants if grant_type(g) == type_name]
