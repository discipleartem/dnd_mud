"""Нормализация grants из YAML (единый формат + legacy features/mechanics)."""

from typing import Any

_ABILITY_BONUS = "ability_bonus"
_ABILITY_INCREASE = "ability_increase"


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
    bonuses = entity.get("inherit_base_bonuses", True)
    features = entity.get("inherit_base_features", True)
    return (
        _coerce_bool(bonuses, True),
        _coerce_bool(features, True),
    )


def normalize_grant(raw: dict[str, Any]) -> dict[str, Any]:
    """Привести grant или legacy mechanics к плоскому виду."""
    grant = dict(raw)
    grant_type = str(grant.get("type", ""))
    if grant_type == _ABILITY_BONUS:
        grant["type"] = _ABILITY_INCREASE
    if "value" in grant and "amount" not in grant:
        grant["amount"] = grant["value"]
    if grant.get("from_list") and not grant.get("from"):
        grant["from"] = grant["from_list"]
    if grant.get("from") == "all_skills":
        grant["from"] = "all"
    return grant


def feature_to_grants(feature: dict[str, Any]) -> list[dict[str, Any]]:
    """Legacy feature → список grants."""
    name = feature.get("name")
    mechanics = feature.get("mechanics", {})
    if isinstance(mechanics, dict) and mechanics:
        merged = dict(mechanics)
        feat_type = feature.get("type")
        if feat_type and "type" not in merged:
            merged["type"] = feat_type
        grant = normalize_grant(merged)
        if name:
            grant["name"] = name
        return [grant]
    feat_type = feature.get("type")
    if feat_type:
        grant = normalize_grant({"type": str(feat_type)})
        if name:
            grant["name"] = name
        return [grant]
    return []


def grants_from_entity(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Grants сущности: ключ grants или legacy features."""
    raw_grants = entity.get("grants", [])
    if isinstance(raw_grants, list) and raw_grants:
        return [normalize_grant(g) for g in raw_grants if isinstance(g, dict)]
    raw_features = entity.get("features", [])
    if not isinstance(raw_features, list):
        return []
    result: list[dict[str, Any]] = []
    for feature in raw_features:
        result.extend(feature_to_grants(feature))
    return result


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
