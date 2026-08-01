"""Нормализация grants из YAML."""

from typing import Any

from core.catalogs.skill_ids import PHB_SKILL_IDS

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


_ARMOR_ALIASES: dict[str, str] = {
    "light_armor": "light",
    "medium_armor": "medium",
    "heavy_armor": "heavy",
}


def normalize_armor_token(token: str) -> str:
    """Привести токен доспеха к light/medium/heavy/shield."""
    return _ARMOR_ALIASES.get(token, token)


def mechanics_from_grant_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Плоский grant или mechanics из class feature."""
    if "mechanics" in entry:
        merged = (
            dict(entry["mechanics"])
            if isinstance(entry["mechanics"], dict)
            else {}
        )
        if entry.get("type") and "type" not in merged:
            merged["type"] = entry["type"]
        return merged
    return dict(entry)


def proficiency_tokens_and_skills_from_grant(
    grant: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Оружие, доспехи, инструменты и навыки из grant."""
    choices = choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    mtype = str(grant.get("type", ""))
    if mtype in ("weapon_proficiency", "bonus_proficiencies"):
        if grant.get("choice"):
            raw = choices.get("weapons", [])
            if isinstance(raw, list):
                weapons.extend(str(w) for w in raw)
        else:
            raw = grant.get("weapons", [])
            if isinstance(raw, list):
                weapons.extend(str(w) for w in raw)
    if mtype in ("armor_proficiency", "bonus_proficiencies"):
        raw = grant.get("armor_types", grant.get("armors", []))
        if isinstance(raw, list):
            armors.extend(normalize_armor_token(str(a)) for a in raw)
    if mtype == "tool_proficiency" and not grant.get("choice"):
        raw = grant.get("tools", [])
        if isinstance(raw, list):
            tools.extend(str(t) for t in raw)
    if mtype == "armor_proficiency":
        raw_w = grant.get("weapons", [])
        if isinstance(raw_w, list):
            weapons.extend(str(w) for w in raw_w)
    if mtype == "skill_proficiency":
        raw = grant.get("skills", [])
        if isinstance(raw, list):
            skills.extend(str(s) for s in raw)
        skill_one = grant.get("skill")
        if isinstance(skill_one, str) and skill_one:
            skills.append(skill_one)
    elif mtype == "multiple_proficiency":
        raw = choices.get("skills_tools", [])
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                kind = entry.get("type", "skill")
                item_id = str(entry.get("id", ""))
                if kind == "tool":
                    tools.append(item_id)
                elif item_id in PHB_SKILL_IDS:
                    skills.append(item_id)
    elif mtype == "skill_expertise":
        raw = choices.get("expertise", [])
        if isinstance(raw, list):
            for item_id in raw:
                sid = str(item_id)
                if sid in PHB_SKILL_IDS:
                    skills.append(sid)
    return weapons, armors, tools, skills


def proficiency_tokens_from_grant(
    grant: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Оружие, доспехи и инструменты из grant."""
    w, a, t, _ = proficiency_tokens_and_skills_from_grant(grant, choices)
    return w, a, t
